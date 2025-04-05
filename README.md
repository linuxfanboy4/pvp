# PVP (Python Package Versioner)  

## Overview  

PVP is a **Python package management system** designed to simplify the publishing, installation, and version control of Python projects. It provides a structured approach to managing Python packages with version tracking, dependency handling, and metadata management.  

## Key Features  

- **Python Package Publishing**: Create distributable packages with versioned releases.  
- **Version Control**: Manage multiple versions of installed Python packages.  
- **Binary Package Creation**: Generate executable package files (`.pv`) for distribution.  
- **Symlink Management**: Maintain clean access to installed packages via symbolic links.  
- **Search Functionality**: Quickly locate installed Python packages.  
- **Cross-platform Support**: Works on Unix-like systems (Linux, macOS) with Python 3.6+.  

## Installation  

To install PVP, run:  

```bash
wget -O /usr/local/bin/pvp https://raw.githubusercontent.com/linuxfanboy4/pvp/refs/heads/main/src/pvp.py && sudo chmod +x /usr/local/bin/pvp
```  

This installs PVP globally, making it available system-wide.  

## System Requirements  

- **Python 3.6 or higher**  
- **Unix-like OS** (Linux, macOS)  
- **Standard utilities** (`tar`, `gzip`, `wget`)  
- **Write permissions** to `/usr/local/bin` and `/usr/local/lib/pvp`  

---  

## Usage  

### Basic Command Structure  

```bash
pvp <command> [arguments]
```  

### Available Commands  

| Command | Description | Usage |  
|---------|------------|-------|  
| `publish` | Publishes a Python package using a `package.pvp` config file. | `pvp publish package.pvp` |  
| `install` | Installs a Python package from a `.pv` file. | `pvp install package-1.0.0.pv` |  
| `uninstall` | Removes an installed Python package. | `pvp uninstall package-name` |  
| `upgrade` | Upgrades an installed package to the latest version. | `pvp upgrade package-name` |  
| `search` | Searches installed Python packages. | `pvp search query` |  

---  

## Package Configuration (`package.pvp`)  

PVP uses an XML-based configuration file (`package.pvp`) to define package metadata.  

### Example `package.pvp`  

```xml
<Package>
    <Name>example-package</Name>
    <Version>1.0.0</Version>
    <Maintainer>Your Name</Maintainer>
    <Description>A Python package example.</Description>
    <RawLink>https://example.com/package.tar.gz</RawLink>
    <Section>Utilities</Section>
</Package>
```  

### Fields  

| Field | Description | Required |  
|-------|-------------|----------|  
| `Name` | Package name (must be unique). | ✅ Yes |  
| `Version` | Semantic version (e.g., `1.0.0`). | ✅ Yes |  
| `Maintainer` | Package author/maintainer. | ✅ Yes |  
| `Description` | Brief package description. | ✅ Yes |  
| `RawLink` | URL to the source `.tar.gz` or `.zip`. | ✅ Yes |  
| `Section` | Category (e.g., `Utilities`, `Dev`). | ❌ No |  

---  

## File System Structure  

PVP organizes packages in the following directories:  

```
/usr/local/bin/            # Symlinks to installed packages (*.pykg)  
/usr/local/lib/pvp/        # Package database  
    packages/              # Package files and metadata  
```  

---  

## Workflow Examples  

### 1. Publishing a Python Package  

1. Create `package.pvp` with metadata.  
2. Run:  
   ```bash
   pvp publish package.pvp
   ```  
3. PVP generates a distributable `.pv` file.  

### 2. Installing a Package  

```bash
pvp install example-package-1.0.0.pv
```  

### 3. Searching Installed Packages  

```bash
pvp search example
```  

### 4. Uninstalling a Package  

```bash
pvp uninstall example-package
```  

---  

## Error Handling & Troubleshooting  

| Issue | Solution |  
|-------|----------|  
| **Permission denied** | Run with `sudo` or ensure write access to `/usr/local`. |  
| **Invalid package format** | Verify the `.pv` or `package.pvp` file structure. |  
| **Download failed** | Check network connectivity and `RawLink` URL. |  
| **Extraction failed** | Ensure the archive (`tar.gz`/`.zip`) is not corrupted. |  

---  

## Security Considerations  

- **Package Verification**: Downloads are checked before extraction.  
- **Strict Permissions**: Installed packages have `755` permissions.  
- **No Auto-Dependencies**: Manual dependency management required.   

## License  

PVP is released under the **MIT License**. Contributions are welcome via GitHub.  
