#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
#
%ifarch sparc
%undefine	with_smp
%endif
#
%define		_rel 1	
Summary:	Zaptel telephony device support
Summary(pl.UTF-8):   Obsługa urządzeń telefonicznych Zaptel
Name:		zaptel
Version:	1.4.0
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://ftp.digium.com/pub/zaptel/releases/%{name}-%{version}.tar.gz
# Source0-md5:	27b43dfa3f1629f063a20779300f68c8
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-make.patch
Patch1:		%{name}-sparc.patch
Patch2:		%{name}-LIBDIR.patch
Patch3:		%{name}-LDFLAGS.patch
Patch4:		%{name}-as_needed-fix.patch
Patch5:		%{name}-sangoma.patch
URL:		http://www.asterisk.org/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
BuildRequires:	newt-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zaptel telephony device driver.

%description -l pl.UTF-8
Sterownik do urządzeń telefonicznych Zaptel.

%package devel
Summary:	Zaptel development headers
Summary(pl.UTF-8):   Pliki nagłówkowe Zaptel
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{_rel}

%description devel
Zaptel development headers.

%description devel -l pl.UTF-8
Pliki nagłówkowe Zaptel.

%package utils
Summary:	Zaptel utility programs
Summary(pl.UTF-8):   Programy narzędziowe Zaptel
Group:		Applications/Communications

%description utils
Zaptel card utility programs, mainly for diagnostics.

%description utils -l pl.UTF-8
Programy narzędziowe do kart Zaptel, służące głównie do diagnostyki.

%package init
Summary:	Zaptel init scripts
Summary(pl.UTF-8):   Skrypty inicjalizujące Zaptel
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
Summary(pl.UTF-8):   Sterownik Zaptel dla jądra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-%{name}
Zaptel telephony Linux kernel driver.

%description -n kernel-%{name} -l pl.UTF-8
Sterownik dla jądra Linuksa do urządzeń telefonicznych Zaptel.

%package -n kernel-smp-%{name}
Summary:	Zaptel Linux SMP kernel driver
Summary(pl.UTF-8):   Sterownik Zaptel dla jądra Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-%{name}
Zaptel telephony Linux SMP kernel driver.

%description -n kernel-smp-%{name} -l pl.UTF-8
Sterownik dla jądra Linuksa SMP do urządzeń telefonicznych Zaptel.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
#%patch1 -p1
#%patch2 -p1
#%patch3 -p1
#%patch4 -p1
%patch5 -p1

%define buildconfigs %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}


%build
%configure

%{__make} prereq zttest \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	OPTFLAGS="%{rpmcflags}"

%if %{with kernel}
for cfg in %{buildconfigs}; do
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
		%{?with_verbose:V=1}
	mv *.ko modules/$cfg/
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
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
for cfg in %{buildconfigs}; do
	cfgdest=''
	if [ "$cfg" = "smp" ]; then
		install modules/$cfg/*.ko \
			$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}$cfg/misc
	else
		install modules/$cfg/*.ko \
			$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
	fi
done
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/sbin,%{_includedir}/linux,/etc/{rc.d/init.d,sysconfig},%{_sbindir},%{_mandir}/{man1,man8}}
%{__make} -o all -o devices install \
	LIBDIR="%{_libdir}" \
	INSTALL_PREFIX=$RPM_BUILD_ROOT \
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

%post -n kernel-smp-%{name}
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-%{name}
%depmod %{_kernel_ver}smp

%if %{with userspace}
%post init
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun init
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc README
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/zaptel.conf
%attr(755,root,root) /sbin/*
%attr(755,root,root) %{_libdir}/*.so.*
%{_mandir}/man8/*

%files init
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/*
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/zaptel

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.so
%{_includedir}/zaptel/
%{_includedir}/zaptel/*.h

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/*
%endif

%if %{with kernel}
%files -n kernel-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp}
%files -n kernel-smp-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif
