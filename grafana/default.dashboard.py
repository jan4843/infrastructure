from grafanalib import formatunits as UNITS
from grafanalib.core import *

x, y, last_h = 0, 0, 0
def POSITION(h, w):
    global x, y, last_h
    if x + w > 24:
        x, y = 0, y + last_h
    position = GridPos(h=h, w=w, x=x, y=y)
    x, last_h = x + w, h
    return dict(gridPos=position)

def COLOR_OVERRIDE(name, color):
    return {
        'matcher': {'id': 'byName', 'options': name},
        'properties': [
            {'id': 'color', 'value': {'mode': 'fixed', 'fixedColor': color}},
        ],
    }

def LINE_DASH_OVERRIDE(name):
    return {
        'matcher': {'id': 'byName', 'options': name},
        'properties': [
            {'id': 'custom.lineStyle', 'value': {'fill': 'dash', 'dash': [20, 10]}},
        ],
    }

LEGEND_SPACER_TARGET = Target(
    expr='0',
    legendFormat=' ',
)
LEGEND_SPACER_OVERRIDE = {
    'matcher': {'id': 'byName', 'options': ' '},
    'properties': [
        {'id': 'color', 'value': {'mode': 'fixed', 'fixedColor': 'transparent'}},
        {'id': 'custom.hideFrom', 'value': {'legend': False, 'tooltip': True, 'viz': True}},
    ],
}

FILL_PARAMS = dict(
    showPoints='never',
    fillOpacity=20,
    gradientMode='opacity',
)

dashboard = Dashboard(
    title='Default',
    sharedCrosshair=True,
    refresh='15s',
    timezone='',
    time=Time('now-1d', 'now'),
    timePicker=TimePicker(
        refreshIntervals=['5s', '15s', '1m'],
        timeOptions=[],
    ),
    templating=Templating(
        list=[
            Template(
                name='host',
                dataSource='grafanacloud-prom',
                query='label_values(node_boot_time_seconds,instance)',
            ),
        ],
    ),
    panels=[
        Stat(
            title='Uptime',
            format=UNITS.SECONDS,
            reduceCalc='lastNotNull',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='node_time_seconds{instance="$host"} - node_boot_time_seconds{instance="$host"}',
                    legendFormat='Uptime',
                ),
            ],
            **POSITION(h=3, w=4),
        ),
        Stat(
            title='Free Root',
            format=UNITS.BYTES_IEC,
            reduceCalc='lastNotNull',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='node_filesystem_avail_bytes{instance="$host",mountpoint="/"}',
                    legendFormat='Free Root',
                ),
            ],
            **POSITION(h=3, w=4),
        ),
        Stat(
            title='Logs Volume',
            format=UNITS.BYTES_IEC,
            reduceCalc='lastNotNull',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-logs',
            targets=[
                Target(
                    expr='sum(bytes_over_time({host="$host"}[$__range]))',
                    legendFormat='Logs Volume',
                ),
            ],
            **POSITION(h=3, w=4),
            links=[
                ExternalLink(
                    title='Loki',
                    uri='/explore?left=%7B%22datasource%22%3A%22grafanacloud-logs%22%2C%22queries%22%3A%5B%7B%22expr%22%3A%22%7Bhost%3D%5C%22${host}%5C%22%7D%22%7D%5D%2C%22range%22%3A%7B%22from%22%3A%22${__from}%22%2C%22to%22%3A%22${__to}%22%7D%7D',
                    keepTime=True,
                ),
            ],
        ),
        Stat(
            title='Containers',
            reduceCalc='lastNotNull',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='count(docker_container_info{instance="$host",state="running"})',
                    legendFormat='Containers',
                ),
            ],
            **POSITION(h=3, w=4),
        ),
        TimeSeries(
            title='Temperature',
            unit=UNITS.CELSUIS,
            legendDisplayMode='hidden',
            **FILL_PARAMS,
            lineInterpolation='smooth',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='max(node_hwmon_temp_celsius{instance="$host"})',
                    legendFormat='Temperature',
                ),
            ],
            **POSITION(h=3, w=8),
        ),

        TimeSeries(
            title='CPU',
            unit=UNITS.PERCENT_UNIT,
            legendDisplayMode='hidden',
            **FILL_PARAMS,
            tooltipMode='multi',
            extraJson={'fieldConfig': {'defaults': {'min': 0, 'max': 1}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='1 - rate(node_cpu_seconds_total{instance="$host",mode="idle"}[$__rate_interval])',
                    legendFormat='CPU {{cpu}}',
                ),
            ],
            **POSITION(h=8, w=12),
        ),
        TimeSeries(
            title='Memory',
            unit=UNITS.BYTES_IEC,
            **FILL_PARAMS,
            lineInterpolation='stepBefore',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-prom',
            stacking={'mode': 'normal', 'group': 'A'},
            targets=[
                Target(
                    expr='node_memory_MemTotal_bytes{instance="$host"} - node_memory_MemFree_bytes{instance="$host"} - node_memory_Cached_bytes{instance="$host"} - node_memory_SReclaimable_bytes{instance="$host"} - node_memory_Buffers_bytes{instance="$host"} - ((node_zfs_arc_c{instance="$host"} - node_zfs_arc_c_min{instance="$host"}) or up * 0)',
                    legendFormat='used',
                ),
                Target(
                    expr='node_memory_Buffers_bytes{instance="$host"}',
                    legendFormat='buffers',
                ),
                Target(
                    expr='node_memory_Cached_bytes{instance="$host"} + node_memory_SReclaimable_bytes{instance="$host"}',
                    legendFormat='cache',
                ),
                Target(
                    expr='(node_zfs_arc_c{instance="$host"} - node_zfs_arc_c_min{instance="$host"}) != 0',
                    legendFormat='zfs',
                ),
                Target(
                    expr='node_memory_MemFree_bytes{instance="$host"}',
                    legendFormat='free',
                ),
            ],
            overrides=[
                COLOR_OVERRIDE('used', 'orange'),
                COLOR_OVERRIDE('buffers', 'purple'), LINE_DASH_OVERRIDE('buffers'),
                COLOR_OVERRIDE('cache', 'yellow'), LINE_DASH_OVERRIDE('cache'),
                COLOR_OVERRIDE('zfs', 'blue'), LINE_DASH_OVERRIDE('zfs'),
                COLOR_OVERRIDE('free', 'green'),
            ],
            **POSITION(h=8, w=12),
        ),
        TimeSeries(
            title='Disk',
            unit=UNITS.BYTES_SEC_IEC,
            legendPlacement='right',
            **FILL_PARAMS,
            lineInterpolation='smooth',
            extraJson={'fieldConfig': {'defaults': {'custom': {'axisCenteredZero': True}}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='-rate(node_disk_read_bytes_total{instance="$host"}[$__rate_interval])',
                    legendFormat='{{device}}',
                ),
                LEGEND_SPACER_TARGET,
                Target(
                    expr='+rate(node_disk_written_bytes_total{instance="$host"}[$__rate_interval])',
                    legendFormat='{{device}}',
                ),
            ],
            overrides=[LEGEND_SPACER_OVERRIDE],
            **POSITION(h=8, w=12),
        ),
        TimeSeries(
            title='Network',
            unit=UNITS.BITS_SEC_IEC,
            legendPlacement='right',
            **FILL_PARAMS,
            lineInterpolation='smooth',
            extraJson={'fieldConfig': {'defaults': {'custom': {'axisCenteredZero': True}}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='8 * -rate(node_network_receive_bytes_total{instance="$host",device!~"(br-|veth).*"}[$__rate_interval]) != 0',
                    legendFormat='{{device}}',
                ),
                LEGEND_SPACER_TARGET,
                Target(
                    expr='8 * +rate(node_network_transmit_bytes_total{instance="$host",device!~"(br-|veth).*"}[$__rate_interval]) != 0',
                    legendFormat='{{device}}',
                ),
            ],
            overrides=[LEGEND_SPACER_OVERRIDE],
            **POSITION(h=8, w=12),
        ),

        RowPanel(
            title='Containers',
            **POSITION(h=1, w=24),
        ),
        TimeSeries(
            title='CPU',
            unit=UNITS.PERCENT_UNIT,
            legendPlacement='right',
            **FILL_PARAMS,
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='rate(docker_container_cpu_seconds_total{instance="$host"}[$__rate_interval])',
                    legendFormat='{{name}}',
                ),
            ],
            **POSITION(h=8, w=12),
        ),
        TimeSeries(
            title='Memory',
            unit=UNITS.BYTES_IEC,
            legendPlacement='right',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            **FILL_PARAMS,
            lineInterpolation='stepBefore',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='sum by (name) (docker_container_memory_usage_bytes{instance="$host"})',
                    legendFormat='{{name}}',
                ),
            ],
            **POSITION(h=8, w=12),
        ),
        TimeSeries(
            title='Disk',
            unit=UNITS.BYTES_SEC_IEC,
            legendPlacement='right',
            **FILL_PARAMS,
            lineInterpolation='smooth',
            extraJson={'fieldConfig': {'defaults': {'custom': {'axisCenteredZero': True}}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='+rate(docker_container_blkio_write_bytes_total{instance="$host"}[$__rate_interval]) != 0',
                    legendFormat='{{name}}',
                ),
                LEGEND_SPACER_TARGET,
                Target(
                    expr='-rate(docker_container_blkio_read_bytes_total{instance="$host"}[$__rate_interval]) != 0',
                    legendFormat='{{name}}',
                ),
            ],
            overrides=[LEGEND_SPACER_OVERRIDE],
            **POSITION(h=8, w=12),
        ),
        TimeSeries(
            title='Network',
            unit=UNITS.BITS_SEC_IEC,
            legendPlacement='right',
            **FILL_PARAMS,
            lineInterpolation='smooth',
            extraJson={'fieldConfig': {'defaults': {'custom': {'axisCenteredZero': True}}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='8 * +rate(docker_container_network_tx_bytes_total{instance="$host"}[$__rate_interval]) != 0',
                    legendFormat='{{name}}',
                ),
                LEGEND_SPACER_TARGET,
                Target(
                    expr='8 * -rate(docker_container_network_rx_bytes_total{instance="$host"}[$__rate_interval]) != 0',
                    legendFormat='{{name}}',
                ),
            ],
            overrides=[LEGEND_SPACER_OVERRIDE],
            **POSITION(h=8, w=12),
        ),
    ],
)
