#
# spec file for package ceph-iscsi
#
# Copyright (C) 2017-2018 The Ceph iSCSI Project Developers. See
# COPYING file at the top-level directory of this distribution and at
# https://github.com/ceph/ceph-iscsi/blob/master/COPYING
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon.
#
# This file is under the GNU General Public License, version 3 or any
# later version.
#
# Please submit bugfixes or comments via http://tracker.ceph.com/
#
%if 0%{?rhel} == 7
%global with_python2 1
%endif


Name:           ceph-iscsi
Version:        3.0
Release:        1%{?dist}
Group:          System/Filesystems
Summary:        Python package providing modules for ceph iscsi gateway configuration management

License:        GPLv3+
URL:            https://github.com/ceph/ceph-iscsi
Source0:        https://github.com/ceph/ceph-iscsi/archive/%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch

Obsoletes:      ceph-iscsi-config
Obsoletes:      ceph-iscsi-cli

%if 0%{?with_python2}
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
Requires:       python-rados >= 10.2.2
Requires:       python-rbd >= 10.2.2
Requires:       python-netifaces >= 0.10.4
Requires:       python-rtslib >= 2.1.fb67
Requires:       rpm-python >= 4.11
Requires:       python-cryptography
Requires:       python-flask >= 0.10.1
%else
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3-rados >= 10.2.2
Requires:       python3-rbd >= 10.2.2
Requires:       python3-netifaces >= 0.10.4
Requires:       python3-rtslib >= 2.1.fb67
Requires:       python3-cryptography
Requires:       python3-flask >= 0.10.1
Requires:       python3-rpm >= 4.11
%endif

BuildRequires:  systemd

%description
Python package providing the modules used to handle the configuration of an
iSCSI gateway, backed by Ceph RBD. The RPM installs configuration management
logic (ceph_iscsi_config modules), an rbd-target-gw systemd service, and
a CLI-based management tool 'gwcli', replacing the 'targetcli' tool.

The configuration management modules may be are consumed by custom Ansible
playbooks and the rbd-target-gw daemon.

The rbd-target-gw service is responsible for startup and shutdown actions,
replacing the 'target' service used in standalone LIO implementations.
In addition, rbd-target-gw also provides a REST API utilized by the Ceph
dashboard and gwcli tool, and a prometheus exporter for gateway LIO
performance statistics, supporting monitoring and visualisation tools like
Grafana.

%prep
%autosetup -p1

%build
%if 0%{?with_python2}
%{__python2} setup.py build
%else
%{py3_build}
%endif

%install
%if 0%{?with_python2}
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}  --install-scripts %{_bindir}
%else
%{py3_install}
%endif
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 .%{_unitdir}/rbd-target-gw.service %{buildroot}%{_unitdir}
install -m 0644 .%{_unitdir}/rbd-target-api.service %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/systemd/system/rbd-target-gw.service.d
install -m 0644 .%{_sysconfdir}/systemd/system/rbd-target-gw.service.d/dependencies.conf %{buildroot}%{_sysconfdir}/systemd/system/rbd-target-gw.service.d/
mkdir -p %{buildroot}%{_mandir}/man8
install -m 0644 gwcli.8 %{buildroot}%{_mandir}/man8/
gzip %{buildroot}%{_mandir}/man8/gwcli.8

%post
/bin/systemctl --system daemon-reload &> /dev/null || :
/bin/systemctl --system enable rbd-target-gw &> /dev/null || :
/bin/systemctl --system enable rbd-target-api &> /dev/null || :

%postun
/bin/systemctl --system daemon-reload &> /dev/null || :

%files
%license LICENSE
%license COPYING
%doc README
%doc iscsi-gateway.cfg_sample
%if 0%{?with_python2}
%{python2_sitelib}/*
%else
%{python3_sitelib}/*
%endif
%{_bindir}/gwcli
%{_bindir}/rbd-target-gw
%{_bindir}/rbd-target-api
%{_unitdir}/rbd-target-gw.service
%{_unitdir}/rbd-target-api.service
%{_sysconfdir}/systemd/system/rbd-target-gw.service.d
%{_mandir}/man8/gwcli.8.gz
%attr(0770,root,root) %dir %{_localstatedir}/log/rbd-target-gw
%attr(0770,root,root) %dir %{_localstatedir}/log/rbd-target-api

%changelog

