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
Version:	0.1
%define	pre 20040407
%define	_rel 0.%{pre}.1
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	%{name}-%{pre}.tar.gz
# Source0-md5:	b3bf72800cf63295e74f03773e04ee8a
Patch0:		%{name}-Makefile.patch
URL:		http://www.asteriskpbx.com
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
BuildRequires:	rpmbuild(macros) >= 1.118
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zaptel telephony device driver.

%description -l pl
Sterownik do urz±dzeñ telefonicznych Zaptel.

%package devel
Summary:	Zaptel development headers
Summary(pl):	Pliki nag³ówkowe Zaptel
Release:	%{_rel}
Group:		Development/Libraries

%description devel
Zaptel development headers.

%description devel -l pl
Pliki nag³ówkowe Zaptel.

%package -n kernel-%{name}
Summary:	Zaptel Linux kernel driver
Summary(pl):	Sterownik Zaptel dla j±dra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?_with_dist_kernel:%requires_releq_kernel_up}
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
%{?_with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-%{name}
Zaptel telephony Linux SMP kernel driver.

%description -n kernel-smp-%{name} -l pl
Sterownik dla j±dra Linuksa SMP do urz±dzeñ telefonicznych Zaptel.

%if %{with userspace}
%package utils
Summary:	Zaptel utility programs
Group:	Applications/Communications

%description utils
Zaptel card utility programs, mainly for diagnostics.
%endif

%prep
%setup -q -n %{name}
%patch0 -p1

%define buildconfigs %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}

%build
%{__make} prereq

%if %{with kernel}
for cfg in %{buildconfigs}; do
	mkdir -p modules/$cfg
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	chmod 000 modules
	%{__make} -C %{_kernelsrcdir} mrproper \
		SUBDIRS=$PWD \
		O=$PWD \
		%{?with_verbose:V=1}
	chmod 700 modules
	install -d include/config
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-${cfg}.h include/linux/autoconf.h
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
%dev(c,196,0) %attr(664,root,root) /dev/zap/ctl
%dev(c,196,1) %attr(664,root,root) /dev/zap/1
%dev(c,196,2) %attr(664,root,root) /dev/zap/2
%dev(c,196,3) %attr(664,root,root) /dev/zap/3
%dev(c,196,4) %attr(664,root,root) /dev/zap/4
%dev(c,196,5) %attr(664,root,root) /dev/zap/5
%dev(c,196,6) %attr(664,root,root) /dev/zap/6
%dev(c,196,7) %attr(664,root,root) /dev/zap/7
%dev(c,196,8) %attr(664,root,root) /dev/zap/8
%dev(c,196,9) %attr(664,root,root) /dev/zap/9
%dev(c,196,10) %attr(664,root,root) /dev/zap/10
%dev(c,196,11) %attr(664,root,root) /dev/zap/11
%dev(c,196,12) %attr(664,root,root) /dev/zap/12
%dev(c,196,13) %attr(664,root,root) /dev/zap/13
%dev(c,196,14) %attr(664,root,root) /dev/zap/14
%dev(c,196,15) %attr(664,root,root) /dev/zap/15
%dev(c,196,16) %attr(664,root,root) /dev/zap/16
%dev(c,196,17) %attr(664,root,root) /dev/zap/17
%dev(c,196,18) %attr(664,root,root) /dev/zap/18
%dev(c,196,19) %attr(664,root,root) /dev/zap/19
%dev(c,196,20) %attr(664,root,root) /dev/zap/20
%dev(c,196,21) %attr(664,root,root) /dev/zap/21
%dev(c,196,22) %attr(664,root,root) /dev/zap/22
%dev(c,196,23) %attr(664,root,root) /dev/zap/23
%dev(c,196,24) %attr(664,root,root) /dev/zap/24
%dev(c,196,25) %attr(664,root,root) /dev/zap/25
%dev(c,196,26) %attr(664,root,root) /dev/zap/26
%dev(c,196,27) %attr(664,root,root) /dev/zap/27
%dev(c,196,28) %attr(664,root,root) /dev/zap/28
%dev(c,196,29) %attr(664,root,root) /dev/zap/29
%dev(c,196,30) %attr(664,root,root) /dev/zap/30
%dev(c,196,31) %attr(664,root,root) /dev/zap/31
%dev(c,196,32) %attr(664,root,root) /dev/zap/32
%dev(c,196,33) %attr(664,root,root) /dev/zap/33
%dev(c,196,34) %attr(664,root,root) /dev/zap/34
%dev(c,196,35) %attr(664,root,root) /dev/zap/35
%dev(c,196,36) %attr(664,root,root) /dev/zap/36
%dev(c,196,37) %attr(664,root,root) /dev/zap/37
%dev(c,196,38) %attr(664,root,root) /dev/zap/38
%dev(c,196,39) %attr(664,root,root) /dev/zap/39
%dev(c,196,40) %attr(664,root,root) /dev/zap/40
%dev(c,196,41) %attr(664,root,root) /dev/zap/41
%dev(c,196,42) %attr(664,root,root) /dev/zap/42
%dev(c,196,43) %attr(664,root,root) /dev/zap/43
%dev(c,196,44) %attr(664,root,root) /dev/zap/44
%dev(c,196,45) %attr(664,root,root) /dev/zap/45
%dev(c,196,46) %attr(664,root,root) /dev/zap/46
%dev(c,196,47) %attr(664,root,root) /dev/zap/47
%dev(c,196,48) %attr(664,root,root) /dev/zap/48
%dev(c,196,49) %attr(664,root,root) /dev/zap/49
%dev(c,196,50) %attr(664,root,root) /dev/zap/50
%dev(c,196,51) %attr(664,root,root) /dev/zap/51
%dev(c,196,52) %attr(664,root,root) /dev/zap/52
%dev(c,196,53) %attr(664,root,root) /dev/zap/53
%dev(c,196,54) %attr(664,root,root) /dev/zap/54
%dev(c,196,55) %attr(664,root,root) /dev/zap/55
%dev(c,196,56) %attr(664,root,root) /dev/zap/56
%dev(c,196,57) %attr(664,root,root) /dev/zap/57
%dev(c,196,58) %attr(664,root,root) /dev/zap/58
%dev(c,196,59) %attr(664,root,root) /dev/zap/59
%dev(c,196,60) %attr(664,root,root) /dev/zap/60
%dev(c,196,61) %attr(664,root,root) /dev/zap/61
%dev(c,196,62) %attr(664,root,root) /dev/zap/62
%dev(c,196,63) %attr(664,root,root) /dev/zap/63
%dev(c,196,64) %attr(664,root,root) /dev/zap/64
%dev(c,196,65) %attr(664,root,root) /dev/zap/65
%dev(c,196,66) %attr(664,root,root) /dev/zap/66
%dev(c,196,67) %attr(664,root,root) /dev/zap/67
%dev(c,196,68) %attr(664,root,root) /dev/zap/68
%dev(c,196,69) %attr(664,root,root) /dev/zap/69
%dev(c,196,70) %attr(664,root,root) /dev/zap/70
%dev(c,196,71) %attr(664,root,root) /dev/zap/71
%dev(c,196,72) %attr(664,root,root) /dev/zap/72
%dev(c,196,73) %attr(664,root,root) /dev/zap/73
%dev(c,196,74) %attr(664,root,root) /dev/zap/74
%dev(c,196,75) %attr(664,root,root) /dev/zap/75
%dev(c,196,76) %attr(664,root,root) /dev/zap/76
%dev(c,196,77) %attr(664,root,root) /dev/zap/77
%dev(c,196,78) %attr(664,root,root) /dev/zap/78
%dev(c,196,79) %attr(664,root,root) /dev/zap/79
%dev(c,196,80) %attr(664,root,root) /dev/zap/80
%dev(c,196,81) %attr(664,root,root) /dev/zap/81
%dev(c,196,82) %attr(664,root,root) /dev/zap/82
%dev(c,196,83) %attr(664,root,root) /dev/zap/83
%dev(c,196,84) %attr(664,root,root) /dev/zap/84
%dev(c,196,85) %attr(664,root,root) /dev/zap/85
%dev(c,196,86) %attr(664,root,root) /dev/zap/86
%dev(c,196,87) %attr(664,root,root) /dev/zap/87
%dev(c,196,88) %attr(664,root,root) /dev/zap/88
%dev(c,196,89) %attr(664,root,root) /dev/zap/89
%dev(c,196,90) %attr(664,root,root) /dev/zap/90
%dev(c,196,91) %attr(664,root,root) /dev/zap/91
%dev(c,196,92) %attr(664,root,root) /dev/zap/92
%dev(c,196,93) %attr(664,root,root) /dev/zap/93
%dev(c,196,94) %attr(664,root,root) /dev/zap/94
%dev(c,196,95) %attr(664,root,root) /dev/zap/95
%dev(c,196,96) %attr(664,root,root) /dev/zap/96
%dev(c,196,97) %attr(664,root,root) /dev/zap/97
%dev(c,196,98) %attr(664,root,root) /dev/zap/98
%dev(c,196,99) %attr(664,root,root) /dev/zap/99
%dev(c,196,100) %attr(664,root,root) /dev/zap/100
%dev(c,196,101) %attr(664,root,root) /dev/zap/101
%dev(c,196,102) %attr(664,root,root) /dev/zap/102
%dev(c,196,103) %attr(664,root,root) /dev/zap/103
%dev(c,196,104) %attr(664,root,root) /dev/zap/104
%dev(c,196,105) %attr(664,root,root) /dev/zap/105
%dev(c,196,106) %attr(664,root,root) /dev/zap/106
%dev(c,196,107) %attr(664,root,root) /dev/zap/107
%dev(c,196,108) %attr(664,root,root) /dev/zap/108
%dev(c,196,109) %attr(664,root,root) /dev/zap/109
%dev(c,196,110) %attr(664,root,root) /dev/zap/110
%dev(c,196,111) %attr(664,root,root) /dev/zap/111
%dev(c,196,112) %attr(664,root,root) /dev/zap/112
%dev(c,196,113) %attr(664,root,root) /dev/zap/113
%dev(c,196,114) %attr(664,root,root) /dev/zap/114
%dev(c,196,115) %attr(664,root,root) /dev/zap/115
%dev(c,196,116) %attr(664,root,root) /dev/zap/116
%dev(c,196,117) %attr(664,root,root) /dev/zap/117
%dev(c,196,118) %attr(664,root,root) /dev/zap/118
%dev(c,196,119) %attr(664,root,root) /dev/zap/119
%dev(c,196,120) %attr(664,root,root) /dev/zap/120
%dev(c,196,121) %attr(664,root,root) /dev/zap/121
%dev(c,196,122) %attr(664,root,root) /dev/zap/122
%dev(c,196,123) %attr(664,root,root) /dev/zap/123
%dev(c,196,124) %attr(664,root,root) /dev/zap/124
%dev(c,196,125) %attr(664,root,root) /dev/zap/125
%dev(c,196,126) %attr(664,root,root) /dev/zap/126
%dev(c,196,127) %attr(664,root,root) /dev/zap/127
%dev(c,196,128) %attr(664,root,root) /dev/zap/128
%dev(c,196,129) %attr(664,root,root) /dev/zap/129
%dev(c,196,130) %attr(664,root,root) /dev/zap/130
%dev(c,196,131) %attr(664,root,root) /dev/zap/131
%dev(c,196,132) %attr(664,root,root) /dev/zap/132
%dev(c,196,133) %attr(664,root,root) /dev/zap/133
%dev(c,196,134) %attr(664,root,root) /dev/zap/134
%dev(c,196,135) %attr(664,root,root) /dev/zap/135
%dev(c,196,136) %attr(664,root,root) /dev/zap/136
%dev(c,196,137) %attr(664,root,root) /dev/zap/137
%dev(c,196,138) %attr(664,root,root) /dev/zap/138
%dev(c,196,139) %attr(664,root,root) /dev/zap/139
%dev(c,196,140) %attr(664,root,root) /dev/zap/140
%dev(c,196,141) %attr(664,root,root) /dev/zap/141
%dev(c,196,142) %attr(664,root,root) /dev/zap/142
%dev(c,196,143) %attr(664,root,root) /dev/zap/143
%dev(c,196,144) %attr(664,root,root) /dev/zap/144
%dev(c,196,145) %attr(664,root,root) /dev/zap/145
%dev(c,196,146) %attr(664,root,root) /dev/zap/146
%dev(c,196,147) %attr(664,root,root) /dev/zap/147
%dev(c,196,148) %attr(664,root,root) /dev/zap/148
%dev(c,196,149) %attr(664,root,root) /dev/zap/149
%dev(c,196,150) %attr(664,root,root) /dev/zap/150
%dev(c,196,151) %attr(664,root,root) /dev/zap/151
%dev(c,196,152) %attr(664,root,root) /dev/zap/152
%dev(c,196,153) %attr(664,root,root) /dev/zap/153
%dev(c,196,154) %attr(664,root,root) /dev/zap/154
%dev(c,196,155) %attr(664,root,root) /dev/zap/155
%dev(c,196,156) %attr(664,root,root) /dev/zap/156
%dev(c,196,157) %attr(664,root,root) /dev/zap/157
%dev(c,196,158) %attr(664,root,root) /dev/zap/158
%dev(c,196,159) %attr(664,root,root) /dev/zap/159
%dev(c,196,160) %attr(664,root,root) /dev/zap/160
%dev(c,196,161) %attr(664,root,root) /dev/zap/161
%dev(c,196,162) %attr(664,root,root) /dev/zap/162
%dev(c,196,163) %attr(664,root,root) /dev/zap/163
%dev(c,196,164) %attr(664,root,root) /dev/zap/164
%dev(c,196,165) %attr(664,root,root) /dev/zap/165
%dev(c,196,166) %attr(664,root,root) /dev/zap/166
%dev(c,196,167) %attr(664,root,root) /dev/zap/167
%dev(c,196,168) %attr(664,root,root) /dev/zap/168
%dev(c,196,169) %attr(664,root,root) /dev/zap/169
%dev(c,196,170) %attr(664,root,root) /dev/zap/170
%dev(c,196,171) %attr(664,root,root) /dev/zap/171
%dev(c,196,172) %attr(664,root,root) /dev/zap/172
%dev(c,196,173) %attr(664,root,root) /dev/zap/173
%dev(c,196,174) %attr(664,root,root) /dev/zap/174
%dev(c,196,175) %attr(664,root,root) /dev/zap/175
%dev(c,196,176) %attr(664,root,root) /dev/zap/176
%dev(c,196,177) %attr(664,root,root) /dev/zap/177
%dev(c,196,178) %attr(664,root,root) /dev/zap/178
%dev(c,196,179) %attr(664,root,root) /dev/zap/179
%dev(c,196,180) %attr(664,root,root) /dev/zap/180
%dev(c,196,181) %attr(664,root,root) /dev/zap/181
%dev(c,196,182) %attr(664,root,root) /dev/zap/182
%dev(c,196,183) %attr(664,root,root) /dev/zap/183
%dev(c,196,184) %attr(664,root,root) /dev/zap/184
%dev(c,196,185) %attr(664,root,root) /dev/zap/185
%dev(c,196,186) %attr(664,root,root) /dev/zap/186
%dev(c,196,187) %attr(664,root,root) /dev/zap/187
%dev(c,196,188) %attr(664,root,root) /dev/zap/188
%dev(c,196,189) %attr(664,root,root) /dev/zap/189
%dev(c,196,190) %attr(664,root,root) /dev/zap/190
%dev(c,196,191) %attr(664,root,root) /dev/zap/191
%dev(c,196,192) %attr(664,root,root) /dev/zap/192
%dev(c,196,193) %attr(664,root,root) /dev/zap/193
%dev(c,196,194) %attr(664,root,root) /dev/zap/194
%dev(c,196,195) %attr(664,root,root) /dev/zap/195
%dev(c,196,196) %attr(664,root,root) /dev/zap/196
%dev(c,196,197) %attr(664,root,root) /dev/zap/197
%dev(c,196,198) %attr(664,root,root) /dev/zap/198
%dev(c,196,199) %attr(664,root,root) /dev/zap/199
%dev(c,196,200) %attr(664,root,root) /dev/zap/200
%dev(c,196,201) %attr(664,root,root) /dev/zap/201
%dev(c,196,202) %attr(664,root,root) /dev/zap/202
%dev(c,196,203) %attr(664,root,root) /dev/zap/203
%dev(c,196,204) %attr(664,root,root) /dev/zap/204
%dev(c,196,205) %attr(664,root,root) /dev/zap/205
%dev(c,196,206) %attr(664,root,root) /dev/zap/206
%dev(c,196,207) %attr(664,root,root) /dev/zap/207
%dev(c,196,208) %attr(664,root,root) /dev/zap/208
%dev(c,196,209) %attr(664,root,root) /dev/zap/209
%dev(c,196,210) %attr(664,root,root) /dev/zap/210
%dev(c,196,211) %attr(664,root,root) /dev/zap/211
%dev(c,196,212) %attr(664,root,root) /dev/zap/212
%dev(c,196,213) %attr(664,root,root) /dev/zap/213
%dev(c,196,214) %attr(664,root,root) /dev/zap/214
%dev(c,196,215) %attr(664,root,root) /dev/zap/215
%dev(c,196,216) %attr(664,root,root) /dev/zap/216
%dev(c,196,217) %attr(664,root,root) /dev/zap/217
%dev(c,196,218) %attr(664,root,root) /dev/zap/218
%dev(c,196,219) %attr(664,root,root) /dev/zap/219
%dev(c,196,220) %attr(664,root,root) /dev/zap/220
%dev(c,196,221) %attr(664,root,root) /dev/zap/221
%dev(c,196,222) %attr(664,root,root) /dev/zap/222
%dev(c,196,223) %attr(664,root,root) /dev/zap/223
%dev(c,196,224) %attr(664,root,root) /dev/zap/224
%dev(c,196,225) %attr(664,root,root) /dev/zap/225
%dev(c,196,226) %attr(664,root,root) /dev/zap/226
%dev(c,196,227) %attr(664,root,root) /dev/zap/227
%dev(c,196,228) %attr(664,root,root) /dev/zap/228
%dev(c,196,229) %attr(664,root,root) /dev/zap/229
%dev(c,196,230) %attr(664,root,root) /dev/zap/230
%dev(c,196,231) %attr(664,root,root) /dev/zap/231
%dev(c,196,232) %attr(664,root,root) /dev/zap/232
%dev(c,196,233) %attr(664,root,root) /dev/zap/233
%dev(c,196,234) %attr(664,root,root) /dev/zap/234
%dev(c,196,235) %attr(664,root,root) /dev/zap/235
%dev(c,196,236) %attr(664,root,root) /dev/zap/236
%dev(c,196,237) %attr(664,root,root) /dev/zap/237
%dev(c,196,238) %attr(664,root,root) /dev/zap/238
%dev(c,196,239) %attr(664,root,root) /dev/zap/239
%dev(c,196,240) %attr(664,root,root) /dev/zap/240
%dev(c,196,241) %attr(664,root,root) /dev/zap/241
%dev(c,196,242) %attr(664,root,root) /dev/zap/242
%dev(c,196,243) %attr(664,root,root) /dev/zap/243
%dev(c,196,244) %attr(664,root,root) /dev/zap/244
%dev(c,196,245) %attr(664,root,root) /dev/zap/245
%dev(c,196,246) %attr(664,root,root) /dev/zap/246
%dev(c,196,247) %attr(664,root,root) /dev/zap/247
%dev(c,196,248) %attr(664,root,root) /dev/zap/248
%dev(c,196,249) %attr(664,root,root) /dev/zap/249
%dev(c,196,250) %attr(664,root,root) /dev/zap/250
%dev(c,196,253) %attr(664,root,root) /dev/zap/timer
%dev(c,196,254) %attr(664,root,root) /dev/zap/channel
%dev(c,196,255) %attr(664,root,root) /dev/zap/pseudo

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.so
/usr/include/*
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

%if %{with userspace}
%files utils
%{_sbindir}/*
%endif
