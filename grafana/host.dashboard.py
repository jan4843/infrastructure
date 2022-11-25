from grafanalib import formatunits as UNITS
from grafanalib.core import *

dashboard = Dashboard(
    title='Host',
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
                query='label_values(host_boot_time, host)',
            ),
        ],
    ),
    panels=[
        Stat(
            title='Uptime',
            format=UNITS.SECONDS,
            reduceCalc='lastNotNull',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='host_uptime{host="$host"}'
                ),
            ],
            gridPos=GridPos(h=4, w=4, x=0, y=0),
        ),
        Stat(
            title='Free Root Filesystem',
            format=UNITS.BYTES_IEC,
            reduceCalc='lastNotNull',
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='host_filesystem_free_bytes{host="$host", mountpoint="/"}'
                ),
            ],
            gridPos=GridPos(h=4, w=4, x=4, y=0),
        ),
        Stat(
            title='Logs Volume',
            format=UNITS.BYTES_IEC,
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            dataSource='grafanacloud-logs',
            targets=[
                Target(
                    expr='sum(bytes_over_time({host="$host"} [$__range]))'
                ),
            ],
            gridPos=GridPos(h=4, w=4, x=8, y=0),
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
            extraJson={'fieldConfig': {'defaults': {'min': 0}}},
            reduceCalc='lastNotNull',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='count(count by(container) (host_container_cpu_usage_seconds_total{host="$host"}))'
                ),
            ],
            gridPos=GridPos(h=4, w=4, x=12, y=0),
        ),
        TimeSeries(
            title='Temperature',
            unit=UNITS.CELSUIS,
            fillOpacity=50,
            gradientMode='opacity',
            showPoints='never',
            legendDisplayMode='hidden',
            lineInterpolation='smooth',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='max(host_sensors_temp_input{host="$host"})',
                    legendFormat='temp',
                ),
            ],
            gridPos=GridPos(h=4, w=8, x=16, y=0),
        ),
        TimeSeries(
            title='CPU',
            unit=UNITS.PERCENT_UNIT,
            showPoints='never',
            legendDisplayMode='hidden',
            fillOpacity=50,
            gradientMode='opacity',
            tooltipMode='multi',
            extraJson={'fieldConfig': {'defaults': {'min': 0, 'max': 1, 'decimals': 1}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='sum by (cpu) (1 - rate(host_cpu_seconds_total{host="$host", mode="idle"}[$__rate_interval]))',
                    legendFormat='{{cpu}}',
                ),
            ],
            gridPos=GridPos(h=8, w=12, x=0, y=4),
        ),
        TimeSeries(
            title='Memory',
            unit=UNITS.BYTES_IEC,
            showPoints='never',
            legendDisplayMode='hidden',
            fillOpacity=50,
            gradientMode='opacity',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='host_memory_total_bytes{host="$host"}',
                    legendFormat='total',
                ),
                Target(
                    expr='host_memory_used_bytes{host="$host"}',
                    legendFormat='used',
                ),
            ],
            gridPos=GridPos(h=8, w=12, x=12, y=4),
        ),
        TimeSeries(
            title='Disk',
            unit=UNITS.BYTES_SEC_IEC,
            showPoints='never',
            fillOpacity=50,
            gradientMode='opacity',
            lineInterpolation='smooth',
            extraJson={'fieldConfig': {'defaults': {'custom': {'axisCenteredZero': True}}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='-sum by (device) (rate(host_disk_read_bytes_total{host="$host", device!~".*[0-9].*"}[$__rate_interval])) != 0',
                    legendFormat='{{device}} read',
                ),
                Target(
                    expr='sum by (device) (rate(host_disk_written_bytes_total{host="$host", device!~".*[0-9].*"}[$__rate_interval])) != 0',
                    legendFormat='{{device}} write',
                ),
            ],
            gridPos=GridPos(h=8, w=12, x=0, y=12),
        ),
        TimeSeries(
            title='Network',
            unit=UNITS.BITS_SEC_IEC,
            showPoints='never',
            fillOpacity=50,
            gradientMode='opacity',
            lineInterpolation='smooth',
            extraJson={'fieldConfig': {'defaults': {'custom': {'axisCenteredZero': True}}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='8 * -sum by (device) (rate(host_network_receive_bytes_total{host="$host"}[$__rate_interval])) != 0',
                    legendFormat='{{device}} download',
                ),
                Target(
                    expr='8 * sum by (device) (rate(host_network_transmit_bytes_total{host="$host"}[$__rate_interval])) != 0',
                    legendFormat='{{device}} upload',
                ),
            ],
            gridPos=GridPos(h=8, w=12, x=12, y=12),
        ),
        TimeSeries(
            title='Containers CPU',
            unit=UNITS.PERCENT_UNIT,
            showPoints='never',
            fillOpacity=50,
            gradientMode='opacity',
            extraJson={'fieldConfig': {'defaults': {'decimals': 1}}},
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='rate(host_container_cpu_usage_seconds_total{host="$host"}[$__rate_interval])',
                    legendFormat='{{container}}',
                ),
            ],
            gridPos=GridPos(h=8, w=12, x=0, y=20),
        ),
        TimeSeries(
            title='Containers Memory',
            unit=UNITS.BYTES_IEC,
            showPoints='never',
            fillOpacity=50,
            gradientMode='opacity',
            dataSource='grafanacloud-prom',
            targets=[
                Target(
                    expr='host_container_memory_anon_bytes{host="$host"}',
                    legendFormat='{{container}}',
                ),
            ],
            gridPos=GridPos(h=8, w=12, x=12, y=20),
        ),
    ],
)
