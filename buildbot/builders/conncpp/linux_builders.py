
################################# bld_linux_connector_cpp ################################

conncpp_linux_step0_checkout= step0_checkout("https://github.com/MariaDB-Corporation/mariadb-connector-cpp.git") + step0_set_test_env
conncpp_linux_step0_ccinstall= linux_ccinstall
conncpp_linux_step1_build= step1_build
conncpp_linux_step2_serverinstall= linux_serverinstall
conncpp_linux_step3_packagetest= """
if [ -d "./src/install_test" ]; then
  cat ./src/install_test/CMakeLists.txt
  mkdir ./install_test
  cd install_test
  cmake ../src/install_test
  cmake --build . --config RelWithDebInfo
  cat ./CMakeFiles/example.dir/link.txt
  PACKLIBS=$(ls $PWD/mariadb-connector-cpp*/lib*/mariadb/libmariadb.*)
  PACKLIBS=$(dirname $PACKLIBS)
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PACKLIBS
  ldd ./example
  readelf -d $PACKLIBS/libmariadbcpp.so*
  ./example "$TEST_UID" "$TEST_PASSWORD" "$SOCKETPATH"
fi
cd ..
"""
conncpp_linux_step4_testsrun= step4_testsrun

def bld_linux_connector_cpp(name, kvm_image, cflags, cmake_params, slaves=connector_slaves):
    linux_connector_cpp= BuildFactory()
    args= ["--port="+getport(), "--user=buildbot", "--smp=4", "--cpu=host"]
    linux_connector_cpp.addStep(ShellCommand(
        description=["cleaning", "build", "dir"],
        descriptionDone=["clean", "build", "dir"],
        command=["sh", "-c", "rm -Rf ../build/*"]))
    linux_connector_cpp.addStep(ShellCommand(
        description=["rsyncing", "VMs"],
        descriptionDone=["rsync", "VMs"],
        doStepIf=(lambda(step): step.getProperty("slavename") != "bb01"),
        haltOnFailure=True,
        command=["rsync", "-a", "-v", "-L",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-build.qcow2",
                 "/kvm/vms/"]))
    linux_connector_cpp.addStep(Compile(
        description=["building", "linux-connctor_cpp"],
        descriptionDone=["build", "linux-connector_cpp"],
        timeout=3600,
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-build.qcow2"] + args +["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        WithProperties("""
export CFLAGS="${CFLAGS}"""+ cflags + """" """ +
conncpp_linux_step0_checkout + """
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCONC_WITH_UNIT_TESTS=Off -DPACKAGE_PLATFORM_SUFFIX=$HOSTNAME""" + cmake_params + """ ../src""" +
conncpp_linux_step1_build +
conncpp_linux_step2_serverinstall +
conncpp_linux_step3_packagetest +
conncpp_linux_step4_testsrun
),
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/build/mariadb*tar.gz .",
        ]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("basename `ls mariadb*tar.gz`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    return {'name': name, 'builddir': name,
            'factory': linux_connector_cpp,
            "slavenames": slaves,
            "category": "connectors"}
######################## bld_linux_connector_cpp - END #####################

def bld_linux_connector_cpp_no_packagetest(name, kvm_image, cflags, cmake_params, slaves=connector_slaves):
    linux_connector_cpp= BuildFactory()
    args= ["--port="+getport(), "--user=buildbot", "--smp=4", "--cpu=host"]
    linux_connector_cpp.addStep(ShellCommand(
        description=["cleaning", "build", "dir"],
        descriptionDone=["clean", "build", "dir"],
        command=["sh", "-c", "rm -Rf ../build/*"]))
    linux_connector_cpp.addStep(ShellCommand(
        description=["rsyncing", "VMs"],
        descriptionDone=["rsync", "VMs"],
        doStepIf=(lambda(step): step.getProperty("slavename") != "bb01"),
        haltOnFailure=True,
        command=["rsync", "-a", "-v", "-L",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-build.qcow2",
                 "/kvm/vms/"]))
    linux_connector_cpp.addStep(Compile(
        description=["building", "linux-connctor_cpp"],
        descriptionDone=["build", "linux-connector_cpp"],
        timeout=3600,
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-build.qcow2"] + args +["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        WithProperties("""
export CFLAGS="${CFLAGS}"""+ cflags + """" """ +
conncpp_linux_step0_checkout + """
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCONC_WITH_UNIT_TESTS=Off -DPACKAGE_PLATFORM_SUFFIX=$HOSTNAME""" + cmake_params + """ ../src""" +
conncpp_linux_step1_build +
conncpp_linux_step2_serverinstall +
conncpp_linux_step4_testsrun
),
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/build/mariadb*tar.gz .",
        ]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("basename `ls mariadb*tar.gz`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    return {'name': name, 'builddir': name,
            'factory': linux_connector_cpp,
            "slavenames": slaves,
            "category": "connectors"}
######################## bld_linux_connector_cpp_no_packagetest - END #####################
######################## "Normal" builders ######################
bld_amd64_asan_connector_cpp= bld_linux_connector_cpp_no_packagetest("ccpp-linux-amd64-asan", "vm-jammy-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_ASAN=ON");
bld_amd64_ubsan_connector_cpp= bld_linux_connector_cpp("ccpp-linux-amd64-ubsan", "vm-jammy-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_UBSAN=ON");
bld_amd64_msan_connector_cpp= bld_linux_connector_cpp("ccpp-linux-amd64-msan", "vm-jammy-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_MSAN=ON");

bld_rhel9_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-rhel9-amd64", "vm-rhel9-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON ");
bld_rhel9_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-rhel9-aarch64", "vm-rhel9-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON ", slaves=connector_slaves_aarch64);

bld_rhel8_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-rhel8-amd64", "vm-rhel8-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON ");
bld_rhel8_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-rhel8-aarch64", "vm-rhel8-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON ", slaves=connector_slaves_aarch64);

bld_rocky8_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-rocky8-aarch64", "vm-rocky8-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON ", slaves=connector_slaves_aarch64);

bld_sles15_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-sles15-amd64", "vm-sles153-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");

bld_focal_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-focal-amd64", "vm-focal-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_focal_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-focal-aarch64", "vm-focal-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON", slaves=connector_slaves_aarch64);

bld_jammy_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-jammy-amd64", "vm-jammy-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_jammy_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-jammy-aarch64", "vm-jammy-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON", slaves=connector_slaves_aarch64);

bld_lunar_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-lunar-amd64", "vm-lunar-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");

bld_mantic_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-mantic-amd64", "vm-mantic-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");

bld_buster_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-buster-amd64", "vm-buster-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_buster_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-buster-aarch64", "vm-buster-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON", slaves=connector_slaves_aarch64);

bld_bullseye_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-bullseye-amd64", "vm-bullseye-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_bullseye_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-bullseye-aarch64", "vm-bullseye-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON", slaves=connector_slaves_aarch64);

bld_bookworm_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-bookworm-amd64", "vm-bookworm-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_bookworm_aarch64_connector_cpp= bld_linux_connector_cpp("ccpp-bookworm-aarch64", "vm-bookworm-aarch64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON", slaves=connector_slaves_aarch64);

bld_fedora37_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-fedora37-amd64", "vm-fedora37-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_fedora38_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-fedora38-amd64", "vm-fedora38-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");
bld_fedora39_amd64_connector_cpp= bld_linux_connector_cpp("ccpp-fedora39-amd64", "vm-fedora39-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON");

##################### Building with the hack for platforms with old gcc ##################

def bld_linux_connector_cpp_with_hack(name, kvm_image, cflags, cmake_params):
    linux_connector_cpp= BuildFactory()
    args= ["--port="+getport(), "--user=buildbot", "--smp=4", "--cpu=host"]
    linux_connector_cpp.addStep(ShellCommand(
        description=["cleaning", "build", "dir"],
        descriptionDone=["clean", "build", "dir"],
        command=["sh", "-c", "rm -Rf ../build/*"]))
    linux_connector_cpp.addStep(ShellCommand(
        description=["rsyncing", "VMs"],
        descriptionDone=["rsync", "VMs"],
        doStepIf=(lambda(step): step.getProperty("slavename") != "bb01"),
        haltOnFailure=True,
        command=["rsync", "-a", "-v", "-L",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-connector.qcow2",
                 "/kvm/vms/"]))
    linux_connector_cpp.addStep(Compile(
        description=["building", "linux-connctor_cpp"],
        descriptionDone=["build", "linux-connector_cpp"],
        timeout=3600,
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-connector.qcow2"] + args +["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        WithProperties("""
export CFLAGS="${CFLAGS}"""+ cflags + """" """ +
conncpp_linux_step0_checkout + """
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCONC_WITH_UNIT_TESTS=Off -DPACKAGE_PLATFORM_SUFFIX=$HOSTNAME""" + cmake_params + """ ../src""" +
conncpp_linux_step1_build +
conncpp_linux_step2_serverinstall +
conncpp_linux_step3_packagetest +
conncpp_linux_step4_testsrun
),
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/build/mariadb*tar.gz .",
        ]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("basename `ls mariadb*tar.gz`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    return {'name': name, 'builddir': name,
            'factory': linux_connector_cpp,
            "slavenames": connector_slaves,
            "category": "connectors"}

bld_centos7_amd64_connector_cpp= bld_linux_connector_cpp_with_hack("ccpp-centos7-amd64", "vm-centos74-amd64", "", " -DWITH_SSL=OPENSSL -DWITH_OPENSSL=ON ");

##################### Building with gcc-5 for platforms with >1 gcc installed, and default is too old  ##################

def bld_linux_connector_cpp_with_gcc5(name, kvm_image, cflags, cmake_params):
    linux_connector_cpp= BuildFactory()
    args= ["--port="+getport(), "--user=buildbot", "--smp=4", "--cpu=host"]
    linux_connector_cpp.addStep(ShellCommand(
        description=["cleaning", "build", "dir"],
        descriptionDone=["clean", "build", "dir"],
        command=["sh", "-c", "rm -Rf ../build/*"]))
    linux_connector_cpp.addStep(ShellCommand(
        description=["rsyncing", "VMs"],
        descriptionDone=["rsync", "VMs"],
        doStepIf=(lambda(step): step.getProperty("slavename") != "bb01"),
        haltOnFailure=True,
        command=["rsync", "-a", "-v", "-L",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-connector.qcow2",
                 "/kvm/vms/"]))
    linux_connector_cpp.addStep(Compile(
        description=["building", "linux-connctor_cpp"],
        descriptionDone=["build", "linux-connector_cpp"],
        timeout=3600,
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-connector.qcow2"] + args +["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        WithProperties("""
export CFLAGS="${CFLAGS}"""+ cflags + """" """ +
conncpp_linux_step0_checkout + """
export CC=/usr/bin/gcc-5
export CXX=/usr/bin/g++-5
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCONC_WITH_UNIT_TESTS=Off -DPACKAGE_PLATFORM_SUFFIX=$HOSTNAME""" + cmake_params + """ ../src""" +
conncpp_linux_step1_build
#+
#conncpp_linux_step2_serverinstall +
#conncpp_linux_step3_packagetest +
#conncpp_linux_step4_testsrun
),
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/build/mariadb*tar.gz .",
        ]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("basename `ls mariadb*tar.gz`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    return {'name': name, 'builddir': name,
            'factory': linux_connector_cpp,
            "slavenames": connector_slaves,
            "category": "connectors"}

bld_sles12_amd64_connector_cpp= bld_linux_connector_cpp_with_gcc5("ccpp-sles12-amd64", "vm-sles125-amd64", "", " -DWITH_SSL=OPENSSL");

##################### RPM/DEB builders ###################

def bld_connector_cpp_rpm(name, kvm_image, cflags, cmake_params):
    linux_connector_cpp= BuildFactory()
    args= ["--port="+getport(), "--user=buildbot", "--smp=4", "--cpu=host"]
    linux_connector_cpp.addStep(ShellCommand(
        description=["cleaning", "build", "dir"],
        descriptionDone=["clean", "build", "dir"],
        command=["sh", "-c", "rm -Rf ../build/*"]))
    linux_connector_cpp.addStep(ShellCommand(
        description=["rsyncing", "VMs"],
        descriptionDone=["rsync", "VMs"],
        doStepIf=(lambda(step): step.getProperty("slavename") != "bb01"),
        haltOnFailure=True,
        command=["rsync", "-a", "-v", "-L",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-build.qcow2",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-install.qcow2",
                 "/kvm/vms/"]))
    linux_connector_cpp.addStep(Compile(
        description=["building", "linux-connctor_cpp"],
        descriptionDone=["build", "linux-connector_cpp"],
        timeout=3600,
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-build.qcow2"] + args +["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        WithProperties("""
export CFLAGS="${CFLAGS}"""+ cflags + """"
mkdir padding_for_CPACK_RPM_BUILD_SOURCE_DIRS_PREFIX
cd padding_for_CPACK_RPM_BUILD_SOURCE_DIRS_PREFIX
""" +
conncpp_linux_step0_ccinstall +
step0_checkout("https://github.com/MariaDB-Corporation/mariadb-connector-cpp.git", False) + """
rm -rf ../src/libmariadb
cd ../build
#-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-L/usr/local/lib/mariadb -I/usr/local/include/mariadb" 
mkdir rpms srpms
cmake -DRPM=On -DCPACK_GENERATOR=RPM -DCMAKE_BUILD_TYPE=RelWithDebInfo -DMARIADB_LINK_DYNAMIC=On -DPACKAGE_PLATFORM_SUFFIX=$HOSTNAME""" + cmake_params + """ ../src
if grep -qw CPACK_RPM_SOURCE_PKG_BUILD_PARAMS CPackSourceConfig.cmake; then
#  cmake --build . --target=package_source
  make package_source
  mv *src*rpm ./srpms/
fi
""" +
conncpp_linux_step1_build + """
mkdir artefacts
mv mariadb*cpp*rpm rpms
mv test/cjportedtests test/sql.properties ./artefacts
ls -l artefacts
"""
),
        "= rm -Rf rpms srpms && mkdir rpms srpms",
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/padding_for_CPACK_RPM_BUILD_SOURCE_DIRS_PREFIX/build/*rpms . && ls ./*rpms",
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/padding_for_CPACK_RPM_BUILD_SOURCE_DIRS_PREFIX/build/artefacts/* ./ && ls ./",
        ]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("cp rpms/*rpm ./ > /dev/null && basename `ls mariadb*cpp*rpm`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    linux_connector_cpp.addStep(Test(
        description=["testing bin rpm", "install"],
        descriptionDone=["test bin rpm", "install"],
        logfiles={"kernel": "kernel_"+getport()+".log"},
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-install.qcow2"] + args + ["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        "= scp -r -P "+getport()+" "+kvm_scpopt+" rpms/mariadb*cpp*rpm ./cjportedtests ./sql.properties buildbot@localhost:buildbot/",
        WithProperties("""
set -ex
ls
cd buildbot
ls
rpm -qlp %(bindistname)s
rpm -qpR %(bindistname)s
#dnf repoquery -l mariadb-connector-c || true
if [ -f /usr/bin/subscription-manager ] ; then sudo subscription-manager refresh ;fi
sudo yum -y --nogpgcheck install %(bindistname)s
""" +
step0_set_test_env + """
ls /usr/lib/*/*maria* /usr/include/maria* || true
""" + conncpp_linux_step2_serverinstall + """
cd buildbot || true
ldd ./cjportedtests
./cjportedtests
""")]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("cp srpms/*rpm ./ > /dev/null && basename `ls mariadb*src*rpm`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    linux_connector_cpp.addStep(Test(
        description=["testing src rpm", "install"],
        descriptionDone=["test src rpm", "install"],
        logfiles={"kernel": "kernel_"+getport()+".log"},
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-install.qcow2"] + args + ["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        "= scp -r -P "+getport()+" "+kvm_scpopt+" rpms srpms/*rpm ./cjportedtests ./sql.properties buildbot@localhost:buildbot/",
        WithProperties("""
set -ex
ls
cd buildbot
ls
rpm -qlp %(bindistname)s
rpm -qpR %(bindistname)s
if [ -f /usr/bin/subscription-manager ] ; then sudo subscription-manager refresh ;fi
sudo dnf --setopt=install_weak_deps=False install -y rpm-build perl-generators
""" + linux_repoinstall + """
sudo dnf --setopt=install_weak_deps=False builddep -y %(bindistname)s || true
rpmbuild --rebuild %(bindistname)s
# removing source rpm - it's not needed any more
rm %(bindistname)s
ls ~/rpmbuild/RPMS || true
# compare requirements to ensure rebuilt rpms got all libraries right
echo rpms/*.rpm           |xargs -n1 rpm -q --requires -p|sed -e 's/>=.*/>=/; s/([A-Z0-9._]*)([0-9]*bit)$//; /MariaDB-compat/d'|sort -u>requires-vendor.txt
echo ~/rpmbuild/RPMS/*.rpm|xargs -n1 rpm -q --requires -p|sed -e 's/>=.*/>=/; s/([A-Z0-9._]*)([0-9]*bit)$//                   '|sort -u>requires-rebuilt.txt
diff -u requires-*.txt

# check if rpm filenames match (won't be true on centos7)
# and if they do, compare more, e.g. file lists and scriptlets

echo "All done"

""" +
step0_set_test_env + """
ls /usr/lib*/*maria* /usr/include/maria* || true
""" + linux_shallow_serverinstall + """
cd buildbot || true
ldd ./cjportedtests
./cjportedtests
""")]))
    return {'name': name, 'builddir': name,
            'factory': linux_connector_cpp,
            "slavenames": connector_slaves,
            "category": "connectors"}

def bld_connector_cpp_deb(name, kvm_image, cflags, cmake_params):
    linux_connector_cpp= BuildFactory()
    args= ["--port="+getport(), "--user=buildbot", "--smp=4", "--cpu=host"]
    linux_connector_cpp.addStep(ShellCommand(
        description=["cleaning", "build", "dir"],
        descriptionDone=["clean", "build", "dir"],
        command=["sh", "-c", "rm -Rf ../build/*"]))
    linux_connector_cpp.addStep(ShellCommand(
        description=["rsyncing", "VMs"],
        descriptionDone=["rsync", "VMs"],
        doStepIf=(lambda(step): step.getProperty("slavename") != "bb01"),
        haltOnFailure=True,
        command=["rsync", "-a", "-v", "-L",
                 "bb01.mariadb.net::kvm/vms/"+kvm_image+"-build.qcow2",
                 "/kvm/vms/"]))
    linux_connector_cpp.addStep(Compile(
        description=["building", "linux-connctor_cpp"],
        descriptionDone=["build", "linux-connector_cpp"],
        timeout=3600,
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-build.qcow2"] + args +["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        WithProperties("""
export CFLAGS="${CFLAGS}"""+ cflags + """" """ +
conncpp_linux_step0_ccinstall +
step0_checkout("https://github.com/MariaDB-Corporation/mariadb-connector-cpp.git", False) + """
rm -rf ../src/libmariadb
cd ../build
#-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-L/usr/local/lib/mariadb -I/usr/local/include/mariadb" 
cmake -DDEB=On -DCPACK_GENERATOR=DEB -DCMAKE_BUILD_TYPE=RelWithDebInfo -DMARIADB_LINK_DYNAMIC=On -DPACKAGE_PLATFORM_SUFFIX=$HOSTNAME -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-L/usr/lib/x86_64-linux-gnu -I/usr/include/mariadb" """ + cmake_params + """ ../src""" +
conncpp_linux_step1_build + """
mkdir artefacts
cp mariadb*cpp*deb test/cjportedtests test/sql.properties ./artefacts
ls -l artefacts
"""
),
        "= scp -r -P "+getport()+" "+kvm_scpopt+" buildbot@localhost:/home/buildbot/build/artefacts/* ./ && ls ./",
        ]))
    linux_connector_cpp.addStep(SetPropertyFromCommand(
        property="bindistname",
        command=["sh", "-c", WithProperties("basename `ls mariadb*cpp*deb`")],
        ))
    addPackageUploadStep(linux_connector_cpp, '"%(bindistname)s"')
    linux_connector_cpp.addStep(Test(
        description=["testing", "install"],
        descriptionDone=["test", "install"],
        logfiles={"kernel": "kernel_"+getport()+".log"},
        env={"TERM": "vt102"},
        command=["runvm", "--base-image=/kvm/vms/"+kvm_image+"-install.qcow2"] + args + ["vm-tmp-"+getport()+".qcow2",
        "rm -Rf buildbot && mkdir buildbot",
        "= scp -r -P "+getport()+" "+kvm_scpopt+" */mariadb*cpp*deb ./cjportedtests ./sql.properties buildbot@localhost:buildbot/",
        WithProperties("""
set -ex
ls
cd buildbot
ls
for i in 1 2 3 ; do
  if sudo apt-get update ; then
      break
  fi
  echo "Installation warning: apt-get update failed, retrying ($i)"
  sleep 6
done
dpkg -c ./%(bindistname)s
sudo sh -c "DEBIAN_FRONTEND=noninteractive apt-get install --allow-unauthenticated -y ./%(bindistname)s"
""" +
step0_set_test_env + """
ls /usr/lib/*/*maria* /usr/include/maria* || true
""" + conncpp_linux_step2_serverinstall + """
cd buildbot || true
ldd ./cjportedtests
# if we want to run tests yet here - we need to install or copy libmariadbcpp.so to some foundable location
#./cjportedtests
""")]))
    return {'name': name, 'builddir': name,
            'factory': linux_connector_cpp,
            "slavenames": connector_slaves,
            "category": "connectors"}

bld_rhel8_x64_connector_cpp_rpm= bld_connector_cpp_rpm("ccpp-rhel8-amd64-rpm", "vm-rhel8-amd64", "", " -DWITH_SSL=OPENSSL");

bld_rhel9_x64_connector_cpp_rpm= bld_connector_cpp_rpm("ccpp-rhel9-amd64-rpm", "vm-rhel9-amd64", "", " -DWITH_SSL=OPENSSL");

bld_cpp_focal_amd64_deb= bld_connector_cpp_deb("ccpp-focal-amd64-deb", "vm-focal-amd64", "", " -DWITH_SSL=OPENSSL");

