odbcMainBuilders=[
                  "codbc-rhel9-amd64", "codbc-windows",
                  "codbc-rhel9-aarch64",
                  "codbc-rhel8-amd64","codbc-alma84-amd64","codbc-alma8-aarch64","codbc-alma9-amd64","codbc-alma9-aarch64",
                  "codbc-rhel8-aarch64",
                  "codbc-rocky8-aarch64",
                  "codbc-focal-amd64",
                  "codbc-focal-amd64-deb", "codbc-jammy-amd64-deb", "codbc-bookworm-amd64-deb", "codbc-bullseye-amd64-deb",
                  "codbc-focal-aarch64-deb", "codbc-jammy-aarch64-deb", "codbc-bookworm-aarch64-deb", "codbc-bullseye-aarch64-deb",
                  "codbc-rhel8-amd64-rpm", "codbc-rhel9-amd64-rpm", "codbc-rhel8-aarch64-rpm", "codbc-rhel9-aarch64-rpm",
                  "codbc-focal-aarch64",
                  "codbc-jammy-amd64", "codbc-bullseye-amd64",
                  "codbc-jammy-aarch64", "codbc-bullseye-aarch64",
                  "codbc-bookworm-aarch64","codbc-bookworm-amd64",
                  "codbc-sles15-amd64", "codbc-sles12-amd64", "codbc-macos",
                  "codbc-fedora39-amd64",
                  "codbc-fedora38-amd64", "codbc-focal-amd64-memcheck",
                  "codbc-source-package",
                  "codbc-linux-amd64-asan", "codbc-linux-amd64-ubsan", "codbc-linux-amd64-msan",
                  "codbc-noble-amd64-deb","codbc-noble-aarch64-deb",
                  ]
cppMainBuilders=[
                  "ccpp-rhel8-amd64",
                  "ccpp-rhel8-aarch64", "ccpp-rocky8-aarch64",
                  "ccpp-alma84-amd64","ccpp-alma9-amd64", "ccpp-alma8-aarch64",  "ccpp-alma9-aarch64",
                  "ccpp-rhel9-amd64",
                  "ccpp-rhel9-aarch64",
                  "ccpp-focal-amd64",
                  "ccpp-focal-aarch64",
                  "ccpp-jammy-amd64", "ccpp-bullseye-amd64",
                  "ccpp-jammy-aarch64", "ccpp-bullseye-aarch64",
                  "ccpp-bookworm-aarch64","ccpp-bookworm-amd64",
                  "ccpp-sles15-amd64", "ccpp-sles12-amd64", "ccpp-macos", 
                  "ccpp-fedora37-amd64",
                  "ccpp-fedora38-amd64",
                  "ccpp-source-package", "ccpp-windows", "ccpp-linux-amd64-asan", "ccpp-linux-amd64-ubsan", "ccpp-linux-amd64-msan",
                  "ccpp-focal-amd64-deb", "ccpp-jammy-amd64-deb", "ccpp-bookworm-amd64-deb", "ccpp-bullseye-amd64-deb",
                  "ccpp-focal-aarch64-deb", "ccpp-jammy-aarch64-deb", "ccpp-bookworm-aarch64-deb", "ccpp-bullseye-aarch64-deb",
                  "ccpp-rhel8-amd64-rpm","ccpp-rhel9-amd64-rpm",
                  "ccpp-rhel8-aarch64-rpm","ccpp-rhel9-aarch64-rpm",
                  "ccpp-noble-amd64-deb","ccpp-noble-aarch64-deb",
                  ]
#c['schedulers'].append(AnyBranchScheduler(
#    name="connector_odbc_maintenance",
#    change_filter=BranchFilter(on_github={"https://github.com/mariadb-corporation/mariadb-connector-odbc/maintenance" : ("3.1")}),
#    treeStableTimer=60,
#    builderNames=odbcMainBuilders))
c['schedulers'].append(AnyBranchScheduler(
    name="connector_odbc",
    change_filter=BranchFilter(on_github={"https://github.com/mariadb-corporation/mariadb-connector-odbc" : ("master", "develop", "maintenance/3.1", "odbc-3.1")}),
    treeStableTimer=60,
    builderNames=odbcMainBuilders))
c['schedulers'].append(AnyBranchScheduler(
    name="connector_cpp",
    change_filter=BranchFilter(on_github={"https://github.com/mariadb-corporation/mariadb-connector-cpp" : ("master", "develop")}),
    treeStableTimer=60,
    builderNames=cppMainBuilders))
odbccppForceBuilderNames= odbcMainBuilders + [
                          "codbc-benchmark",
                          "codbc-sles15-amd64-notest",
                          "codbc-windows-gnutls"
                          ##########################################################################
                          ] + cppMainBuilders
