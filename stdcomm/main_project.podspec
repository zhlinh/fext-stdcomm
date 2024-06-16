Pod::Spec.new do |spec|
    spec.name                     = 'main_project'
    spec.version                  = '1.0'
    spec.homepage                 = 'Link to the Module'
    spec.source                   = { :http=> ''}
    spec.authors                  = ''
    spec.license                  = ''
    spec.summary                  = 'Some description for the Shared Module'
    spec.vendored_frameworks      = 'cmake_build/iOS/Darwin.out/*.*framework', 'third_party/*comm/lib/ios/*.*framework'
    spec.vendored_libraries       = 'third_party/**comm/lib/ios/*.a'
    spec.libraries                = 'c++', "z"
    spec.frameworks               = "SystemConfiguration"
    spec.ios.deployment_target = '14.1'
                
                
    spec.pod_target_xcconfig = {
        'KOTLIN_PROJECT_PATH' => ':main_project',
        'PRODUCT_MODULE_NAME' => 'main_project',
    }
                
    spec.script_phases = [
        {
            :name => 'Build common',
            :execution_position => :before_compile,
            :shell_path => '/bin/sh',
            :script => <<-SCRIPT
                if [ "YES" = "$COCOAPODS_SKIP_KOTLIN_BUILD" ]; then
                  echo "Skipping Gradle build task invocation due to COCOAPODS_SKIP_KOTLIN_BUILD environment variable set to \"YES\""
                  exit 0
                fi
                set -ev
                REPO_ROOT="$PODS_TARGET_SRCROOT"
                # Get the absolute path of the repo root
                REPO_ROOT_ABS=$(cd "$REPO_ROOT" && pwd)
                echo "REPO_ROOT_ABS: $REPO_ROOT_ABS"
                last_dir="$(pwd)"
                cd "$REPO_ROOT_ABS" && python3 build_ios.py 1
                cd "$last_dir"
            SCRIPT
        }
    ]
                
end