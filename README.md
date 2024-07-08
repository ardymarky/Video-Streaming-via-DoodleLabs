# Video-Streaming-via-DoodleLabs

The DoodleLabs in Cwean has an Ip address of 10.223.168.25.
Cwean has an IP address of 10.223.168.1. THIS is the IP to use for Gstreamer.

Whatever device is being used as the computer, its ip address is what Gstreamer uses, NOT doodlelabs' ip address.

### USB Camera

Client Side (sending):

`gst-launch-1.0 v4l2src device=/dev/video2 ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegparse ! rtpjpegpay ! udpsink host=10.223.168.1 port=5000 sync=false` 

Host Side (receiving):

`gst-launch-1.0 -v udpsrc port=5004 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)JPEG, payload=(int)26" ! rtpjpegdepay ! jpegdec ! videoconvert ! ximagesink sync=false`


### Thermal Camera

Client Side (sending): 

`gst-launch-1.0 -v v4l2src device=/dev/video1 ! video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 ! nvvidconv ! 'video/x-raw(memory:NVMM), format=I420' ! omxh264enc control-rate=2 bitrate=2000000 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=10.223.168.25 port=5004`


Host Side (receiving):

`gst-launch-1.0 -v udpsrc port=5004 ! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink`
