#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
#
Summary:	Zaptel telephony device support
Summary(pl):	Obs³uga urz±dzeñ telefonicznych Zaptel
Name:		zaptel
Version:	0.9.1
%define	_rel	4
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	ftp://ftp.asterisk.org/pub/telephony/zaptel/%{name}-%{version}.tar.gz
# Source0-md5:	8833bdaf0670b4b5f48e4823887be8d5
Patch0:		%{name}-Makefile.patch
URL:		http://www.asteriskpbx.com
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zaptel telephony device driver.

%description -l pl
Sterownik do urz±dzeñ telefonicznych Zaptel.

%package devel
Summary:	Zaptel development headers
Summary(pl):	Pliki nag³ówkowe Zaptel
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

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
Programy narzêdziowe do kart Zaptel, s³u¿±ce g³ównie do
diagnostyki.

%package -n kernel-%{name}
Summary:	Zaptel Linux kernel driver
Summary(pl):	Sterownik Zaptel dla j±dra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-%{name}
Zaptel telephony Linux kernel driver.

%description -n kernel-%{name} -l pl
Sterownik dla j±dra Linuksa do urz±dzeñ telefonicznych Zaptel.

%package -n kernel-smp-%{name}
Summary:	Zaptel Linux SMP kernel driver
Summary(pl):	Sterownik Zaptel dla j±dra Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-%{name}
Zaptel telephony Linux SMP kernel driver.

%description -n kernel-smp-%{name} -l pl
Sterownik dla j±dra Linuksa SMP do urz±dzeñ telefonicznych Zaptel.

%prep
%setup -q
%patch0 -p1

%define buildconfigs %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}

%build
%{__make} prereq \
	CC="%{__cc}"

%if %{with kernel}
for cfg in %{buildconfigs}; do
	mkdir -p modules/$cfg
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	chmod 000 modules
	install -d include/{linux,config}
	%{__make} -C %{_kernelsrcdir} clean \
		SUBDIRS=$PWD \
		O=$PWD \
		%{?with_verbose:V=1}
	install -d include/config
	chmod 700 modules
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-${cfg}.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm #FIXME
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} modules \
		SUBDIRS=$PWD \
		O=$PWD \
		%{?with_verbose:V=1}
	mv *.ko modules/$cfg/
done
%endif

%if %{with userspace}
%{__make} ztcfg torisatool makefw ztmonitor ztspeed
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
install -d $RPM_BUILD_ROOT{/sbin,/usr/include/linux,/etc,%{_sbindir}}
%{__make} -o all -o devices install \
	INSTALL_PREFIX=$RPM_BUILD_ROOT
install torisatool makefw ztmonitor ztspeed $RPM_BUILD_ROOT%{_sbindir}
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
%files
%defattr(644,root,root,755)
%doc README ChangeLog
%attr(600,root,root) /etc/zaptel.conf
%attr(755,root,root) /sbin/*
%attr(755,root,root) %{_libdir}/*.so.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.so
/usr/include/*

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/*
%endif

%if %{with kernel}
%files -n kernel-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*

%if %{with smp}
%files -n kernel-smp-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
