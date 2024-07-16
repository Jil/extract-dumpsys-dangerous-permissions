# ChatGPT 4o generated script with iterative prompts to parse a dumpsys 
# extraction looking for sensitive permissions in use. 
# Alternative outputs are commented out in the code.

# List of sensitive permissions extracted from https://developer.android.com/reference/android/Manifest.permission
# with "Protection level: dangerous" on 2024-08-16

import re
import sys
from collections import defaultdict

# List of commonly recognized sensitive permissions
sensitive_permissions = [
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    "android.permission.CAMERA",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_PHONE_STATE",
    "android.permission.CALL_PHONE",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.USE_SIP",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.BODY_SENSORS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECEIVE_MMS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.ACTIVITY_RECOGNITION",
    "android.permission.READ_MEDIA_AUDIO",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.POST_NOTIFICATIONS"
]

def parse_dumpsys(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    packages = re.findall(r'Package \[(.*?)\] \((.*?)\):\n(.*?)(?=Package \[|$)', content, re.DOTALL)
    package_permissions = {}
    permission_to_packages = defaultdict(list)
    sensitive_permission_to_packages = defaultdict(list)
    runtime_permissions = defaultdict(dict)

    for package in packages:
        package_name = package[0]
        package_content = package[2]
        
        install_permissions_match = re.search(r'install permissions:\n(.*?)(?=User \d+:|$)', package_content, re.DOTALL)
        runtime_permissions_match = re.search(r'runtime permissions:\n(.*?)(?=User \d+:|$)', package_content, re.DOTALL)
        
        if install_permissions_match:
            install_permissions = install_permissions_match.group(1).strip()
            granted_install_permissions = [line.split(':')[0].strip() for line in install_permissions.split('\n') if 'granted=true' in line]
            package_permissions[package_name] = '\n'.join(granted_install_permissions)

            # Collect each granted install permission and map it to the package
            for permission in granted_install_permissions:
                permission_to_packages[permission].append(package_name)
                if permission in sensitive_permissions:
                    sensitive_permission_to_packages[permission].append(package_name)
        
        if runtime_permissions_match:
            runtime_perms = runtime_permissions_match.group(1).strip()
            granted_runtime_permissions = [line.split(':')[0].strip() for line in runtime_perms.split('\n') if 'granted=true' in line]
            runtime_permissions[package_name] = '\n'.join(granted_runtime_permissions)

            # Collect each granted runtime permission and map it to the package
            for permission in granted_runtime_permissions:
                permission_to_packages[permission].append(package_name)
                if permission in sensitive_permissions:
                    sensitive_permission_to_packages[permission].append(package_name)

    return package_permissions, permission_to_packages, sensitive_permission_to_packages, runtime_permissions

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_permissions.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    package_permissions, permission_to_packages, sensitive_permission_to_packages, runtime_permissions = parse_dumpsys(file_path)

    # print("Packages and their Install Permissions (Granted=True):")
    # print("="*40)
    # for package, permissions in package_permissions.items():
    #     print(f"Package: {package}")
    #     print("Install Permissions:")
    #     print(permissions)
    #     print("="*40)
    
    # print("\nPackages and their Runtime Permissions (Granted=True):")
    # print("="*40)
    # for package, permissions in runtime_permissions.items():
    #     print(f"Package: {package}")
    #     print("Runtime Permissions:")
    #     print(permissions)
    #     print("="*40)
    
    # print("\nPermissions and Packages that have them enabled (Granted=True):")
    # print("="*40)
    # for permission, packages in permission_to_packages.items():
    #     print(f"Permission: {permission}")
    #     print("Packages:")
    #     for pkg in packages:
    #         print(f"  - {pkg}")
    #     print("="*40)

    print("\nSensitive Permissions and Packages that have them enabled (Granted=True):")
    print("="*40)
    for permission, packages in sensitive_permission_to_packages.items():
        print(f"Sensitive Permission: {permission}")
        print("Packages:")
        for pkg in packages:
            print(f"  - {pkg}")
        print("="*40)

if __name__ == "__main__":
    main()
