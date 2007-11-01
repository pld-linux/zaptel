# TODO
# - sparc, ppc fail
# - zaptel-1.2.15/ztdummy.c:103:2: warning: #warning This module will not be usable since the kernel HZ setting is not 1000 ticks per second.
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
%bcond_with	grsec_kernel	# build for kernel-grsecurity

%ifarch sparc
%undefine	with_smp
%endif

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		_rel	2
Summary:	Zaptel telephony device support
Summary(pl):	Obs³uga urz±dzeñ telefonicznych Zaptel
Name:		zaptel
Version:	1.2.21
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://downloads.digium.com/pub/zaptel/%{name}-%{version}.tar.gz
# Source0-md5:	262186d4749adbbabc5b96a0d1c3c70e
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-make.patch
Patch1:		%{name}-sparc.patch
Patch4:		%{name}-as_needed-fix.patch
Patch5:		%{name}-sangoma.patch
URL:		http://www.asterisk.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build}
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
%if %{with userspace}
BuildRequires:	newt-devel
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	modules_1	pciradio,tor2,torisa,wcfxo,wct1xxp,wct4xxp/wct4xxp,
%define	modules_2	wctdm,wcte11xp,wcusb,zaptel,ztd-eth,ztd-loc,ztdummy,ztdynamic

# modules added in 1.2.15 (see r1.75.2.2)
%ifnarch ppc alpha sparc
%define	modules_1_2_15  wctc4xxp/wctc4xxp,wcte12xp,xpp/{xpd_fxo,xpd_fxs,xpp,xpp_usb},zttranscode
%endif

%define	modules		%{modules_1},%{modules_2}%{?modules_1_2_15:,%{modules_1_2_15}}

%description
Zaptel telephony device driver.

%description -l pl
Sterownik do urz±dzeñ telefonicznych Zaptel.

%package devel
Summary:	Zaptel development headers
Summary(pl):	Pliki nag³ówkowe Zaptel
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{_rel}
# files in /usr/include/linux
Requires:	linux-libc-headers

%description devel
Zaptel development headers.

%description devel -l pl
Pliki nag³ówkowe Zaptel.

%package utils
Summary:	Zaptel utility programs
Summary(pl):	Programy narzêdziowe Zaptel
Group:		Applications/Communications

%description utils
Zaptel card utility programs, mainly for diagnostics.

%description utils -l pl
Programy narzêdziowe do kart Zaptel, s³u¿±ce g³ównie do diagnostyki.

%package init
Summary:	Zaptel init scripts
Summary(pl):	Skrypty inicjalizuj±ce Zaptel
Group:		Applications/Communications
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-utils = %{version}-%{_rel}
Requires:	rc-scripts

%description init
Zaptel boot-time initialization.

%description init -l pl
Inicjalizacja Zaptel w czasie startu systemu.

%package -n kernel%{_alt_kernel}-%{name}
Summary:	Zaptel Linux kernel driver
Summary(pl):	Sterownik Zaptel dla j±dra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-%{name}
Zaptel telephony Linux kernel driver.

%description -n kernel%{_alt_kernel}-%{name} -l pl
Sterownik dla j±dra Linuksa do urz±dzeñ telefonicznych Zaptel.

%package -n kernel%{_alt_kernel}-smp-%{name}
Summary:	Zaptel Linux SMP kernel driver
Summary(pl):	Sterownik Zaptel dla j±dra Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-smp-%{name}
Zaptel telephony Linux SMP kernel driver.

%description -n kernel%{_alt_kernel}-smp-%{name} -l pl
Sterownik dla j±dra Linuksa SMP do urz±dzeñ telefonicznych Zaptel.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch4 -p1
%patch5 -p1

%build
%{__make} prereq zttest \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	OPTFLAGS="%{rpmcflags}"

%if %{with kernel}
echo : {%{modules},}
%build_kernel_modules SUBDIRS=$PWD -m %{modules}
%endif

%if %{with userspace}
%{__make} ztcfg torisatool makefw ztmonitor ztspeed libtonezone.so \
	fxstest fxotune gendigits \
	CC="%{__cc} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m %{modules} -d misc
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/sbin,%{_includedir}/linux,/etc/{rc.d/init.d,sysconfig},%{_sbindir},%{_mandir}/{man1,man8}}
%{__make} -o all -o devices -o modules install \
	LIBDIR="%{_libdir}" \
	DESTDIR=$RPM_BUILD_ROOT \
	KMAKE_INST= \
	SBINDIR=%{_sbindir} \
	MODCONF=$RPM_BUILD_ROOT/etc/modprobe.conf
install makefw fxstest gendigits $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/zaptel
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/zaptel
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-%{name}
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-%{name}
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-%{name}
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-%{name}
%depmod %{_kernel_ver}smp

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
%doc README ChangeLog
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/zaptel.conf
%attr(755,root,root) %{_sbindir}/ztcfg
%attr(755,root,root) %{_libdir}/*.so.*
%{_mandir}/man8/*

%files init
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/*
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/zaptel

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.so
%{_includedir}/linux/*
%{_includedir}/*.h

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/fxotune
%attr(755,root,root) %{_sbindir}/fxstest
%attr(755,root,root) %{_sbindir}/gendigits
%attr(755,root,root) %{_sbindir}/makefw
%attr(755,root,root) %{_sbindir}/torisatool
%attr(755,root,root) %{_sbindir}/ztmonitor
%attr(755,root,root) %{_sbindir}/ztspeed
%attr(755,root,root) %{_sbindir}/zttest
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif
