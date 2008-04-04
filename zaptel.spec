#
# TODO:
# - update to kernel macros
# Installed (but unpackaged) file(s) found:
#   /etc/hotplug/usb/xpp_fxloader
#   /etc/hotplug/usb/xpp_fxloader.usermap
#   /etc/udev/rules.d/xpp.rules
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
%bcond_with	oslec		# with Open Source Line Echo Canceller
%bcond_with	bristuff	# with bristuff support

%ifarch sparc
%undefine	with_smp
%endif

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		rel	4
%define		pname	zaptel
Summary:	Zaptel telephony device support
Summary(pl.UTF-8):	Obsługa urządzeń telefonicznych Zaptel
Name:		%{pname}%{_alt_kernel}
Version:	1.4.8
Release:	%{rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://ftp.digium.com/pub/zaptel/releases/%{pname}-%{version}.tar.gz
# Source0-md5:	f57e1ba86a3dd4ef141ca3831e11c076
Source1:	%{pname}.init
Source2:	%{pname}.sysconfig
Source3:	http://ftp.digium.com/pub/telephony/firmware/releases/zaptel-fw-oct6114-064-1.05.01.tar.gz
# Source3-md5:	18e6e6879070a8d61068e1c87b8c2b22
Source4:	http://ftp.digium.com/pub/telephony/firmware/releases/zaptel-fw-oct6114-128-1.05.01.tar.gz
# Source4-md5:	c46a13f468b53828dc5c78f0eadbefd4
Source5:	http://ftp.digium.com/pub/telephony/firmware/releases/zaptel-fw-tc400m-MR5.6.tar.gz
# Source5-md5:	ec5c96f7508bfb0e0b8be768ea5f3aa2
Source6:	http://downloads.digium.com/pub/telephony/firmware/releases/zaptel-fw-vpmadt032-1.07.tar.gz
# Source6-md5:	7916c630a68fcfd38ead6caf9b55e5a1
Patch0:		%{pname}-make.patch
Patch1:		%{pname}-sangoma.patch
Patch2:		%{pname}-oslec.patch
Patch3:		%{pname}-bristuff.patch
URL:		http://www.asterisk.org/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
BuildRequires:	module-init-tools
%endif
BuildRequires:	newt-devel
BuildRequires:	perl-base
BuildRequires:	perl-tools-pod
BuildRequires:	rpmbuild(macros) >= 1.379
%{?with_bristuff:Provides:	zaptel(bristuff)}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zaptel telephony device driver.

%description -l pl.UTF-8
Sterownik do urządzeń telefonicznych Zaptel.

%package devel
Summary:	Zaptel development headers
Summary(pl.UTF-8):	Pliki nagłówkowe Zaptel
Group:		Development/Libraries
Requires:	%{pname} = %{version}-%{rel}
%{?with_bristuff:Provides:	zaptel-devel(bristuff)}

%description devel
Zaptel development headers.

%description devel -l pl.UTF-8
Pliki nagłówkowe Zaptel.

%package static
Summary:	Zaptel static library
Summary(pl.UTF-8):	Biblioteka statyczna Zaptel
Group:		Development/Libraries
Requires:	%{pname}-devel = %{version}-%{rel}
%{?with_bristuff:Provides:	zaptel-static(bristuff)}

%description static
Zaptel static library.

%description static -l pl.UTF-8
Biblioteka statyczna Zaptel.

%package utils
Summary:	Zaptel utility programs
Summary(pl.UTF-8):	Programy narzędziowe Zaptel
Group:		Applications/Communications

%description utils
Zaptel card utility programs, mainly for diagnostics.

%description utils -l pl.UTF-8
Programy narzędziowe do kart Zaptel, służące głównie do diagnostyki.

%package init
Summary:	Zaptel init scripts
Summary(pl.UTF-8):	Skrypty inicjalizujące Zaptel
Group:		Applications/Communications
Requires(post,preun):	/sbin/chkconfig
Requires:	%{pname}-utils = %{version}-%{rel}
Requires:	rc-scripts

%description init
Zaptel boot-time initialization.

%description init -l pl.UTF-8
Inicjalizacja Zaptel w czasie startu systemu.

%package -n kernel%{_alt_kernel}-%{pname}
Summary:	Zaptel Linux kernel driver
Summary(pl.UTF-8):	Sterownik Zaptel dla jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%{?with_oslec:Requires:	kernel-misc-oslec = 20070608-0.1@%{_kernel_ver_str}}
%endif

%description -n kernel%{_alt_kernel}-%{pname}
Zaptel telephony Linux kernel driver.

%description -n kernel%{_alt_kernel}-%{pname} -l pl.UTF-8
Sterownik dla jądra Linuksa do urządzeń telefonicznych Zaptel.

%package -n perl-Zaptel
Summary:	Perl interface to Zaptel
Summary(pl.UTF-8):	Perlowy interfejs do Zaptela
Group:		Development/Languages/Perl
Requires:	%{pname} = %{version}-%{rel}

%description -n perl-Zaptel
Perl inferface to Zaptel.

%description -n perl-Zaptel -l pl.UTF-8
Perlowy interfejs do Zaptela.

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1
%patch1 -p1
%{?with_oslec:%patch2 -p1}
%{?with_bristuff:%patch3 -p1}

%define buildconfigs %{?with_dist_kernel:dist}%{!?with_dist_kernel:nondist}

%build
%configure

%{__make} prereq zttest \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	OPTFLAGS="%{rpmcflags}" \
	KSRC=%{_kernelsrcdir}

%if %{with kernel}
cp %{SOURCE3} firmware
cp %{SOURCE4} firmware
cp %{SOURCE5} firmware
cp %{SOURCE6} firmware
cd firmware
for t in *.tar.gz; do
	tar -xzf $t
done
cd ..
for cfg in %{buildconfigs}; do
	rm -rf o
	mkdir -p modules/$cfg
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	chmod 000 modules
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1} \
		KSRC=%{_kernelsrcdir}
	install -d o/include/config
	chmod 700 modules
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD/o SUBDIRS=$PWD \
		DOWNLOAD=wget \
		ZAP="-I$(pwd)" \
		%{?with_verbose:V=1} \
		KSRC=%{_kernelsrcdir}
	cp *.ko %{?with_bristuff:*/*.ko} modules/$cfg/
done
%endif

%if %{with userspace}
%{__make} ztcfg torisatool makefw ztmonitor ztspeed %{?with_bristuff:ztpty} libtonezone.so \
	fxstest fxotune \
	CC="%{__cc} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}" \
	KSRC=%{_kernelsrcdir}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
for cfg in %{buildconfigs}; do
	cfgdest=''
	install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
	install modules/$cfg/*.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
done
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/sbin,%{_includedir}/linux,/etc/{rc.d/init.d,sysconfig},%{_sbindir},%{_mandir}/{man1,man8}}
%{__make} -o all -o devices -j1 install \
	LIBDIR="%{_libdir}" \
	LIB_DIR="%{_libdir}" \
	INSTALL_PREFIX=$RPM_BUILD_ROOT \
	DESTDIR=$RPM_BUILD_ROOT \
	MODCONF=$RPM_BUILD_ROOT/etc/modprobe.conf \
	KSRC=%{_kernelsrcdir} \
	PERLLIBDIR=%{perl_vendorlib}
install zttest torisatool makefw ztmonitor ztspeed fxstest fxotune %{?with_bristuff:ztpty} $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/zaptel
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/zaptel
touch $RPM_BUILD_ROOT/etc/zaptel.conf

install zconfig.h ecdis.h fasthdlc.h biquad.h $RPM_BUILD_ROOT/usr/include/zaptel/
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-%{pname}
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-%{pname}
%depmod %{_kernel_ver}

%post init
/sbin/chkconfig --add %{pname}
%service %{pname} restart

%preun init
if [ "$1" = "0" ]; then
	%service %{pname} stop
	/sbin/chkconfig --del %{pname}
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/zaptel.conf
%attr(755,root,root) /sbin/*
%attr(755,root,root) %{_libdir}/*.so.*
%{_datadir}/zaptel
%{_mandir}/man8/*

%files init
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/*
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/zaptel

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.so
%{_includedir}/zaptel

%files static
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.a

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-%{pname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif

%files -n perl-Zaptel
%defattr(644,root,root,755)
%{perl_vendorlib}/Zaptel
%{perl_vendorlib}/Zaptel.pm
