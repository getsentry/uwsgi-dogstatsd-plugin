# don't use this it doesn't work!

it turns out the `uwsgi` struct changes pretty significantly based on the
compilation options meaning plugins need to be compiled against the specific
uwsgi build that's used at runtime

___

uwsgi-dogstatsd-plugin
======================

a pip-installable version of [uwsgi-dogstatsd]

[uwsgi-dogstatsd]: https://github.com/DataDog/uwsgi-dogstatsd
