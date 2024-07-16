# Video-Streaming-via-DoodleLabs

The DoodleLabs in Cwean has an Ip address of 10.223.168.25.
Cwean has an IP address of 10.223.168.1. THIS is the IP to use for Gstreamer.

Whatever device is being used as the computer, its ip address is what Gstreamer uses, NOT doodlelabs' ip address.

### USB Camera

Client Side (sending):

`gst-launch-1.0 v4l2src device=/dev/video2 ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! videoconvert ! x264enc tune=zerolatency bitrate=5000 speed-preset=superfast ! rtph264pay ! udpsink host=10.223.168.1 port=5001 sync=false` 


Host Side (receiving):

`gst-launch-1.0 udpsrc port=5001 caps="application/x-rtp,media=video,clock-rate=90000,encoding-name=H264" ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false`


### Thermal Camera

Client Side (sending): 

`gst-launch-1.0 -v v4l2src device=/dev/video1 ! video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 ! nvvidconv ! 'video/x-raw(memory:NVMM), format=I420' ! omxh264enc control-rate=2 bitrate=2000000 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=10.223.168.25 port=5004`


Host Side (receiving):

`gst-launch-1.0 -v udpsrc port=5004 ! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink`


### LiDAR (not working yet)


Client Side (sending):
``` terminal
source blickfeld/install/setup.bash
mkfifo /tmp/ros2_to_gst
ros2 topic echo /bf_lidar/point_cloud_out --truncate-length 200000 > /tmp/ros2_to_gst
```

`GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0/ gst-launch-1.0 -v filesrc location=/tmp/ros2_to_gst ! gzenc ! udpsink host=<receiver_ip> port=5000 sync=false`
or
`GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0/ gst-launch-1.0 -v filesrc location=/tmp/ros2_to_gst ! gzenc ! tcpclientsink host=<receiver_ip> port=5000`

Host Side (receiving):

`GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0/ gst-launch-1.0 -v udpsrc port=5000 ! gzenc ! filesink location=<file-location>.txt`
or
`GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0/ gst-launch-1.0 -v tcpserversrc host=0.0.0.0 port=5000 ! queue ! gzdec ! filesink location=<file-location>.txt

https://github.com/Snec/gst-gz
https://stackoverflow.com/questions/75418645/using-gstream-with-fifo
https://www.gnu.org/software/libc/manual/html_node/Pipes-and-FIFOs.html
