#
# TODO:
# - IMPORTANT rename: http://www.asterisk.org/zaptel-to-dahdi
#
# - kernel modules doesn't build
# - should more header files be installed?
# - Installed (but unpackaged) file(s) found:
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
%bcond_without	xpp		# without Astribank
%bcond_with	verbose

%ifarch sparc
%undefine	with_smp
%endif
%ifarch alpha
%undefine	with_xpp
%endif

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	27
%define		pname	zaptel
%define		FIRMWARE_URL http://downloads.digium.com/pub/telephony/firmware/releases
Summary:	Zaptel telephony device support
Summary(pl.UTF-8):	Obsługa urządzeń telefonicznych Zaptel
Name:		%{pname}%{_alt_kernel}
Version:	1.4.12.1
Release:	%{rel}%{?with_bristuff:.bristuff}
License:	GPL
Group:		Base/Kernel
Source0:	http://ftp.digium.com/pub/zaptel/releases/%{pname}-%{version}.tar.gz
# Source0-md5:	71e83a020b020fa60905edecf70e95a3
Source1:	%{pname}.init
Source2:	%{pname}.sysconfig
Source3:	%{FIRMWARE_URL}/zaptel-fw-oct6114-064-1.05.01.tar.gz
# Source3-md5:	18e6e6879070a8d61068e1c87b8c2b22
Source4:	%{FIRMWARE_URL}/zaptel-fw-oct6114-128-1.05.01.tar.gz
# Source4-md5:	c46a13f468b53828dc5c78f0eadbefd4
Source5:	%{FIRMWARE_URL}/zaptel-fw-vpmadt032-1.07.tar.gz
# Source5-md5:	7916c630a68fcfd38ead6caf9b55e5a1
Source6:	%{FIRMWARE_URL}/zaptel-fw-tc400m-MR6.12.tar.gz
# Source6-md5:	c57f41fae88f129e14fcaf41e4df90dc
Patch0:		%{pname}-make.patch
Patch1:		%{pname}-oslec.patch
Patch2:		%{pname}-bristuff.patch
Patch3:		%{pname}-sparc.patch
Patch4:		%{pname}-kernel.patch
URL:		http://www.asterisk.org/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build
BuildRequires:	module-init-tools
%endif
BuildRequires:	newt-devel
BuildRequires:	perl-base
BuildRequires:	perl-tools-pod
BuildRequires:	rpmbuild(macros) >= 1.379
%{?with_bristuff:Provides:	zaptel(bristuff)}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# Rules:
# - modules_X: single modules, just name module with no suffix
# - modules_X: subdir modules are just directory name with slash like dirname/
# - keep X and X_in in sync
# - X is used for actual building (entries separated with space), X_in for pld macros (entries separated with comma)

%define	modules_1	zaptel.o ztd-eth.o ztd-loc.o pciradio.o tor2.o torisa.o wcfxo.o wct1xxp.o wctdm.o wcte11xp.o wcusb.o ztdummy.o ztdynamic.o
%define	modules_1_in	zaptel,ztd-eth,ztd-loc,pciradio,tor2,torisa,wcfxo,wct1xxp,wctdm,wcte11xp,wcusb,ztdummy,ztdynamic

%define	modules_2	wct4xxp/ wcte12xp/ %{?with_xpp:xpp/}
%define	modules_2_in	wct4xxp/wct4xxp,wcte12xp/wcte12xp%{?with_xpp:,xpp/{%{?with_bristuff:xpd_bri,}xpd_fxo,xpd_fxs,xpd_pri,xpp,xpp_usb}}
%ifnarch alpha
%define	modules_nalpha	wctc4xxp/ wctdm24xxp/ zttranscode.o
%define	modules_nalpha_in	wctc4xxp/wctc4xxp,wctdm24xxp/wctdm24xxp,zttranscode
%endif
%if %{with bristuff}
%define	modules_bristuff cwain/ qozap/ vzaphfc/ zaphfc/ ztgsm/ opvxa1200.o wcopenpci.o
%define	modules_bristuff_in	cwain/cwain,qozap/qozap,vzaphfc/vzaphfc,zaphfc/zaphfc,ztgsm/ztgsm,opvxa1200,wcopenpci
%endif
%define	modules		%{modules_1} %{modules_2}%{?modules_nalpha: %{modules_nalpha}}%{?modules_bristuff: %{modules_bristuff}}
%define	modules_in	%{modules_1_in},%{modules_2_in}%{?modules_nalpha:,%{modules_nalpha_in}}%{?modules_bristuff:,%{modules_bristuff_in}}

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
%{?with_oslec:%patch1 -p1}
%{?with_bristuff:%patch2 -p1}
%patch3 -p1
%patch4 -p1

%if %{with kernel}
for a in %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE6}; do
	ln -s $a firmware
	tar -C firmware -xzf $a
done

cat > download-logger <<'EOF'
#!/bin/sh
# keep log of files make wanted to download in firmware/ dir
echo "$@" >> download.log
EOF
chmod a+rx download-logger
%endif

%build
if [ ! -f configure.stamp ]; then
	rm -f configure.stamp
	%configure
	%{__make} prereq zttest \
		CC="%{__cc}" \
		LDFLAGS="%{rpmldflags}" \
		OPTFLAGS="%{rpmcflags}"
	touch configure.stamp
fi

%if %{with kernel}
%build_kernel_modules SUBDIRS=$PWD DOWNLOAD=$PWD/download-logger ZAP="-I$PWD" KSRC=%{_kernelsrcdir} KBUILD_OBJ_M="%{modules}" -m %{modules_in} -C kernel

check_modules() {
	err=0
	for a in kernel/{*/,}*.ko; do
		[[ $a = *-dist.ko ]] && continue
		[[ $a = *-up.ko ]] && continue
		[[ $a = *-smp.ko ]] && continue
		echo >&2 "unpackaged module: ${a%.ko}"
		err=1
	done

	[ $err = 0 ] || exit 1
}
check_modules
%endif

%if %{with userspace}
%{__make} zttool zttest ztmonitor ztspeed sethdlc-new ztcfg \
	ztcfg-dude fxstest fxotune ztdiag torisatool \
	%{?with_bristuff:ztpty} libtonezone.so \
	CC="%{__cc} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}" \
	KSRC=%{_kernelsrcdir}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
cd kernel
%install_kernel_modules -m %{modules_in} -d misc
cd ..
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
install zttool zttest ztmonitor ztspeed sethdlc-new ztcfg ztcfg-dude fxstest fxotune ztdiag torisatool %{?with_bristuff:ztpty} $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/zaptel
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/zaptel
touch $RPM_BUILD_ROOT/etc/zaptel.conf

install kernel/{zconfig.h,ecdis.h,fasthdlc.h,biquad.h} $RPM_BUILD_ROOT/usr/include/zaptel/
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
%if %{with xpp}
%{_datadir}/zaptel
%endif
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

%if %{with xpp}
%files -n perl-Zaptel
%defattr(644,root,root,755)
%{perl_vendorlib}/Zaptel
%{perl_vendorlib}/Zaptel.pm
%endif
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-%{pname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif
