FILE(GLOB_RECURSE app_sources ${CMAKE_SOURCE_DIR}/src/*.*)
idf_component_register(SRCS ${app_sources} ${CMAKE_SOURCE_DIR}/lib/session_guard/session_guard.c
                       INCLUDE_DIRS ${CMAKE_SOURCE_DIR}/lib/session_guard)
