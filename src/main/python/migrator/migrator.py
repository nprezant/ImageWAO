from base import ctx, config, Version

from .individualmigrators import IndividualMigrators


currentVersion = ctx.version()
versionHistory = [Version(0, 0, 0), Version(0, 3, 0)]


class Migrator:
    def migrate(self):
        appVersion = Version.fromString(ctx.version())
        projectVersion = config.projectVersion()

        if projectVersion == appVersion:
            return

        elif projectVersion > appVersion:
            raise EnvironmentError(
                "Software out of date."
                f"App version: {appVersion}; "
                f"Project version: {projectVersion}"
            )

        elif projectVersion < appVersion:
            migrators = IndividualMigrators()
            upgradeStart = versionHistory.index(projectVersion) + 1
            upgradesToMake = versionHistory[upgradeStart:]
            for upgradeVersion in upgradesToMake:
                print(f"Upgrading to {upgradeVersion.toString()}")
                upgradeCallableName = f"migrate{upgradeVersion.major}_{upgradeVersion.minor}_{upgradeVersion.patch}"
                try:
                    upgradeCallable = getattr(migrators, upgradeCallableName)
                except AttributeError:
                    raise RuntimeError(
                        f"Migrator not configured to upgrade to {upgradeCallableName}"
                    )
                else:
                    upgradeCallable()
                    config.setProjectVersion(upgradeVersion)
