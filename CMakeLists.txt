cmake_minimum_required(VERSION 2.6)
project(leakless)

set(VULN vuln.c)
set(EXPLOIT return-to-dl/exploit.py)

# Compiler flags
# ==============

# Global flags
# ------------

set(CMAKE_C_FLAGS "-fno-stack-protector -O2")
set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")

# Architectures and related options
# ---------------------------------

set(ARCHITECTURES "x86;x86-64" CACHE STRING "List of architectures to enable")

if ("${CMAKE_C_COMPILER_ID}" STREQUAL "Clang")
  set(INTEL_FLAVOR "-mllvm --x86-asm-syntax=intel")
elseif ("${CMAKE_C_COMPILER_ID}" STREQUAL "GNU")
  set(INTEL_FLAVOR "-masm=intel")
endif()

set(x86_FLAGS "${INTEL_FLAVOR} -m32")
set(x86_OFFSET "112")

set(x86-64_FLAGS "${INTEL_FLAVOR} -m64")
set(x86-64_OFFSET "120")

# Build types and related options
# -------------------------------

set(BUILD_TYPES no_relro partial_relro full_relro)

set(NO_RELRO_FLAGS "")
set(PARTIAL_RELRO_FLAGS "-Wl,-z,relro")
set(FULL_RELRO_FLAGS "-Wl,-z,relro,-z,now")

# Testing
# =======

enable_testing()

set(TEST_TYPES craft-dl-structs ld-corrupt)

set(TEST_FLAGS_craft-dl-structs "--method=craft-dl-structs")
set(TEST_FLAGS_ld-corrupt "--method=ld-corrupt -l 1")

# List of tests expected to fail
# ------------------------------

set(EXPECTED_TO_FAIL test-craft-dl-structs-vuln-x86-full_relro test-craft-dl-structs-vuln-x86-64-full_relro)

# Helper library
# ==============

# We create a helper library to avoid issues with RELRO libcs/loaders

set(HELPER_C_FILE "${CMAKE_CURRENT_BINARY_DIR}/helper.c")
file(WRITE "${HELPER_C_FILE}" "int return42() { return 42; }")
foreach(ARCHITECTURE ${ARCHITECTURES})
  set(TARGET_NAME "helper-${ARCHITECTURE}")
  add_library("${TARGET_NAME}" SHARED "${HELPER_C_FILE}")
  set_target_properties("${TARGET_NAME}" PROPERTIES
    COMPILE_FLAGS "${${ARCHITECTURE}_FLAGS}"
    LINK_FLAGS "${${ARCHITECTURE}_FLAGS}")
endforeach(ARCHITECTURE)

# Create targets
# ==============

add_custom_target(length)
add_custom_target(json)
add_custom_target(ropl)

foreach(ARCHITECTURE ${ARCHITECTURES})
  foreach(BUILD_TYPE ${BUILD_TYPES})

    # Binaries
    # --------

    set(TARGET_NAME "vuln-${ARCHITECTURE}-${BUILD_TYPE}")
    string(TOUPPER "${BUILD_TYPE}" TYPE_PREFIX)
    add_executable("${TARGET_NAME}" "${VULN}")
    target_link_libraries("${TARGET_NAME}" "helper-${ARCHITECTURE}")
    set_target_properties("${TARGET_NAME}" PROPERTIES
      COMPILE_FLAGS "${${ARCHITECTURE}_FLAGS} ${${TYPE_PREFIX}_FLAGS}"
      LINK_FLAGS "${${ARCHITECTURE}_FLAGS} ${${TYPE_PREFIX}_FLAGS}")

    # Tests
    # -----

    foreach(TEST_TYPE ${TEST_TYPES})
      set(TEST_NAME "test-${TEST_TYPE}-${TARGET_NAME}")
      set(TEST_FLAGS "${TEST_FLAGS_${TEST_TYPE}}")
      # Invoke the exploit
      set(EXPLOIT_INVOCATION "${CMAKE_SOURCE_DIR}/${EXPLOIT} ${TEST_FLAGS} --offset ${${ARCHITECTURE}_OFFSET} $<TARGET_FILE:${TARGET_NAME}>")
      # Command to execute and check of correctness
      set(TEST_INVOCATION "(${EXPLOIT_INVOCATION}; echo '/bin/bash -c \"base64 -d <<< UGFzc2VkCg==\"') | $<TARGET_FILE:${TARGET_NAME}> | grep -E '^Passed$'")

      # If we expect failure of this test, negate the exit result
      list(FIND EXPECTED_TO_FAIL "${TEST_NAME}" EXPECTED_TO_FAIL_INDEX)
      if (NOT EXPECTED_TO_FAIL_INDEX EQUAL -1)
        set(TEST_INVOCATION "! (${TEST_INVOCATION})")
      endif()

      # Add the test
      add_test(NAME "${TEST_NAME}" COMMAND /bin/sh -c "${TEST_INVOCATION}")

      # Add the target to have the length
      set(TARGET_LEGTH_NAME "length-${TEST_TYPE}-${TARGET_NAME}")
      add_custom_target("${TARGET_LEGTH_NAME}" COMMAND /bin/sh -c "${EXPLOIT_INVOCATION} --size")
      add_dependencies(length "${TARGET_LEGTH_NAME}")

      add_custom_command(OUTPUT "${TEST_TYPE}-${TARGET_NAME}.json"
        COMMAND /bin/sh -c "${EXPLOIT_INVOCATION} -o json" > ${TEST_TYPE}-${TARGET_NAME}.json)
      add_custom_target("json-${TEST_TYPE}-${TARGET_NAME}" DEPENDS "${TEST_TYPE}-${TARGET_NAME}.json")
      add_dependencies(json "json-${TEST_TYPE}-${TARGET_NAME}")

      add_custom_command(OUTPUT "${TEST_TYPE}-${TARGET_NAME}.ropl"
        COMMAND /bin/sh -c "${EXPLOIT_INVOCATION} -o ropl" > ${TEST_TYPE}-${TARGET_NAME}.ropl)
      add_custom_target("ropl-${TEST_TYPE}-${TARGET_NAME}" DEPENDS "${TEST_TYPE}-${TARGET_NAME}.ropl")
      add_dependencies(ropl "ropl-${TEST_TYPE}-${TARGET_NAME}")

    endforeach(TEST_TYPE)

  endforeach(BUILD_TYPE)
endforeach(ARCHITECTURE)
