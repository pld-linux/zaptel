#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
#
%define	_rel	1
Summary:	Zaptel telephony device support
Summary(pl.UTF-8):	Obsługa urządzeń telefonicznych Zaptel
Name:		zaptel
Version:	1.4.3
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://ftp.digium.com/pub/zaptel/releases/%{name}-%{version}.tar.gz
# Source0-md5:	e00685ff2cd081b63a62a3d9cd9a4c0a
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	http://ftp.digium.com/pub/telephony/firmware/releases/zaptel-fw-oct6114-064-1.05.01.tar.gz
# Source3-md5:	18e6e6879070a8d61068e1c87b8c2b22
Source4:	http://ftp.digium.com/pub/telephony/firmware/releases/zaptel-fw-oct6114-128-1.05.01.tar.gz
# Source4-md5:	c46a13f468b53828dc5c78f0eadbefd4
Patch0:		%{name}-make.patch
Patch1:		%{name}-sangoma.patch
Patch2:		%{name}-oslec.patch
URL:		http://www.asterisk.org/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	newt-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zaptel telephony device driver.

%description -l pl.UTF-8
Sterownik do urządzeń telefonicznych Zaptel.

%package devel
Summary:	Zaptel development headers
Summary(pl.UTF-8):	Pliki nagłówkowe Zaptel
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{_rel}

%description devel
Zaptel development headers.

%description devel -l pl.UTF-8
Pliki nagłówkowe Zaptel.

%package static
Summary:	Zaptel static library
Summary(pl.UTF-8):	Biblioteka statyczna Zaptel
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{_rel}

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
Requires:	%{name}-utils = %{version}-%{_rel}
Requires:	rc-scripts

%description init
Zaptel boot-time initialization.

%description init -l pl.UTF-8
Inicjalizacja Zaptel w czasie startu systemu.

%package -n kernel-%{name}
Summary:	Zaptel Linux kernel driver
Summary(pl.UTF-8):	Sterownik Zaptel dla jądra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel-%{name}
Zaptel telephony Linux kernel driver.

%description -n kernel-%{name} -l pl.UTF-8
Sterownik dla jądra Linuksa do urządzeń telefonicznych Zaptel.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%define buildconfigs %{?with_dist_kernel:dist}%{!?with_dist_kernel:nondist}

%build
%configure

%{__make} prereq zttest \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	OPTFLAGS="%{rpmcflags}"

%if %{with kernel}
cp %{SOURCE3} firmware/
cp %{SOURCE4} firmware/
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
		%{?with_verbose:V=1}
	install -d o/include/config
	chmod 700 modules
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD/o SUBDIRS=$PWD \
		DOWNLOAD=wget \
		%{?with_verbose:V=1}
	cp *.ko modules/$cfg/
done
%endif

%if %{with userspace}
%{__make} ztcfg torisatool makefw ztmonitor ztspeed libtonezone.so \
	fxstest fxotune \
	CC="%{__cc} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"
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
%{__make} -o all -o devices install \
	LIBDIR="%{_libdir}" \
	LIB_DIR="$RPM_BUILD_ROOT%{_libdir}" \
	INSTALL_PREFIX=$RPM_BUILD_ROOT \
	DESTDIR=$RPM_BUILD_ROOT \
	MODCONF=$RPM_BUILD_ROOT/etc/modprobe.conf
install zttest torisatool makefw ztmonitor ztspeed fxstest fxotune $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/zaptel
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/zaptel

install zconfig.h ecdis.h fasthdlc.h biquad.h $RPM_BUILD_ROOT/usr/include/zaptel/
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-%{name}
%depmod %{_kernel_ver}

%postun -n kernel-%{name}
%depmod %{_kernel_ver}

%post init
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun init
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
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
%files -n kernel-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif
