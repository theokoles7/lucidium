#!/usr/bin/env python3
"""
# Automatic version bumping script for Lucidium.

## Usage:
    >>> python scripts/bump_version.py patch        # 1.0.0 -> 1.0.1
    >>> python scripts/bump_version.py minor        # 1.0.0 -> 1.1.0
    >>> python scripts/bump_version.py major        # 1.0.0 -> 2.0.0
    >>> python scripts/bump_version.py --to 1.2.3   # Set specific version
"""

from argparse   import ArgumentParser, Namespace
from pathlib    import Path
from re         import match, Match, search, sub
from subprocess import CalledProcessError, run
from typing     import Literal, Tuple

class VersionBumber():
    """# Version Bumber.
    
    Handles version bumping for Lucidium project.
    """
    
    def __init__(self,
        project_root:   Path =  None
    ):
        """# Instantiate Version Bumber.

        ## Args:
            * project_root (Path, optional): Root of project. Defaults to None.
        """
        # Define paths.
        self._project_root_:    Path =  project_root or Path(__file__).parent.parent
        self._version_file_:    Path =  self._project_root_ / "lucidium" / "_version_.py"
        
    # METHODS ======================================================================================
    
    def bump_version(self,
        current:    str,
        bump_type:  Literal["major", "minor", "patch"]
    ) -> str:
        """# Bump Version.

        ## Args:
            * current   (str):  Current version being bumped.
            * bump_type (str):  Type of version bump. Must be "major", "minor", or "patch".

        ## Returns:
            * str:  Bumped version.
        """
        # Parse current version.
        major, minor, patch = self.parse_version(version = current)
        
        # Match bump type.
        match bump_type:
            
            # Return major bump.
            case "major":   return f"{major + 1}.0.0"
            
            # Return minor bump.
            case "minor":   return f"{major}.{minor + 1}.0"
            
            # Return patch bump.
            case "patch":   return f"{major}.{minor}.{patch + 1}"
            
            # Report invalid bump type.
            case _:         raise ValueError(f"Invalid version bump type: {bump_type}")
    
    def get_current_version(self) -> str:
        """# Get Current Version..

        ## Returns:
            * str:  Project's current version.
        """
        # If version file, does not exist...
        if not self._version_file_.exists():
            
            # Report error.
            raise FileNotFoundError(f"Version file not found: {self._version_file_}")
        
        # Match version data.
        match:  Match = search(r"""__version__ = ["\']([^"\']+)["\']""", self._version_file_.read_text())
        
        # If version was not found...
        if not match:
            
            # Report error.
            raise ValueError(f" Could not find version in {self._version_file_}")
        
        # Provide version.
        return match.group(1)
    
    def parse_version(self,
        version:    str
    ) -> Tuple[int, int, int]:
        """# Parse Version.

        ## Args:
            * version   (str):  Version string being parsed.

        ## Returns:
            * Tuple[int, int, int]: Tuple representing major, minor, and patch version components.
        """
        try:# Parse version.
            major, minor, patch = map(int, version.split("."))
            
            # Return components.
            return major, minor, patch
        
        # If format was invalid.
        except ValueError:
            
            # Report error.
            raise ValueError(f"Invalid versino format: {version}")
        
    def tag_version(self,
        version:    str,
        message:    str =   None
    ) -> None:
        """# Tag Version.

        ## Args:
            * version   (str):  Version being tagged.
            * message   (str):  Description of version.
        """
        try:# Ensure that current location is within repository.
            run(["git", "rev-parse", "--git-dir"], check = True, capture_output = True, cwd = self._project_root_)
            
            # Track version file.
            run(["git", "add", str(self._version_file_)], check = True, cwd = self._project_root_)
            
            # Commit version update.
            run(["git", "commit", "-m", (message or f"Bump version to {version}")], check = True, cwd = self._project_root_)
            
            # Tag version update.
            run(["git", "tag", "-a", f"v{version}", "-m", f"Release {version}"], check = True, cwd = self._project_root_)
            
            # Report successful tag.
            print(f"Created git tag: v{version}")
            print(f"Run 'git push && git push --tags' to push to remote")
            
        # If process fails...
        except CalledProcessError as e:
            
            # Report error.
            print(f"Git operation failed: {e}")
            print("Version was updated, but not committed/tagged.")
            
        # If Git is not installed.
        except FileNotFoundError:
            
            # Report error.
            print("Git installation not found. Version was updated, but not committed/tagged.")
        
    def update_version_file(self,
        new_version:    str
    ) -> None:
        """# Update Version File.

        ## Args:
            * new_version   (str):  New version.
        """
        # Update file with new version.
        self._version_file_.write_text(
            sub(
                r"""__version__ = ["\'][^"\']+["\']""",
                f"""__version__ = "{new_version}" """,
                self._version_file_.read_text()
            )
        )
        
        # Report update.
        print(f"""Updated {self._version_file_} to v{new_version}""")
        
    def validate_version(self,
        version:    str
    ) -> bool:
        """# Validate Version Format.

        ## Args:
            * version   (str):  Version being validated.

        ## Returns:
            * bool: True if version is valid.
        """
        # Validate version.
        return  bool(match(
                    r"""^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?(?:\+[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?$""",
                    version
                ))
        

def main(*args, **kwargs) -> None:
    """# Execute Version Update."""    
    # Define parser.
    _parser_:   ArgumentParser =    ArgumentParser(description = "Bum Lucidium version.")
    
    # Define arguments.
    _parser_.add_argument(
        "bump_type",
        type =      str,
        choices =   ["major", "minor", "patch"],
        nargs =     "?",
        help =      """Type of version bump. Must be "major", "minor", or "patch"."""
    )
    
    _parser_.add_argument(
        "--version", "-v",
        type =      str,
        help =      """Override to specific version."""
    )
    
    _parser_.add_argument(
        "--message", "-m",
        type =      str,
        help =      """Version commit message."""
    )
    
    _parser_.add_argument(
        "--no-git",
        action =    "store_true",
        default =   False,
        help =      "Don't create git commit/tag."
    )
    
    _parser_.add_argument(
        "--dry-run",
        action =    "store_true",
        default =   False,
        help =      """Validate version bump without writing to file."""
    )
    
    # Parse arguments.
    _args_:     Namespace =         _parser_.parse_args()
    
    # If neither bumpt type or version override are provided...
    if _args_.bump_type is None and _args_.version is None:
        
        # Report error.
        _parser_.error("Must specify either bump type or a version override.")
        
    # If both bump type and version override are provided...
    if _args_.bump_type is not None and _args_.version is not None:
        
        # Report error.
        _parser_.error("Cannot specify both bump type and version override.")
        
    # Instantiate version bump utility.
    _bumper_:   VersionBumber =     VersionBumber()
    
    try:# Get current version.
        current_version:    str =   _bumper_.get_current_version()
        
        # Communicate version fetched.
        print(f"Current version: {current_version}")
        
        # If version override was provided...
        if _args_.version:
            
            # If the version provided is not valid...
            if not _bumper_.validate_version(version = _args_.version):
                
                # Report error.
                print(f"ERROR: Invalid version format: {_args_.version}")
                
                # Indicate failure.
                exit(1)
                
            # Otherwise, new version will the one provided by override.
            updated_version:    str =   _args_.version
            
        # Otherwise...
        else:
            
            # Form new version based on bump type.
            updated_version:    str =   _bumper_.bump_version(
                                            current =   current_version,
                                            bump_type = _args_.bump_type
                                        )
            
        # Communicate new version.
        print(f"Updated version: {updated_version}")
        
        # If this is just a dry run, simply return.
        if _args_.dry_run: return
        
        # Otherwise, carry on to file update.
        _bumper_.update_version_file(new_version = updated_version)
        
        # Unless it's requested that no commit/tag be made...
        if not _args_.no_git:
            
            # Commit & tag version update.
            _bumper_.tag_version(
                version =   updated_version,
                message =   _args_.message
            )
            
        # Report successful update.
        print(f"Version bump successful: {current_version} -> {updated_version}")
        
    # If any errors occur...
    except Exception as e:
        
        # Report error.
        print(f"ERROR: {e}")
        
        # Indicate failure.
        exit(1)
        

if __name__ == "__main__": main()