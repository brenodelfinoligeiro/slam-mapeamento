cmake_minimum_required(VERSION 3.8)
project(simulador_base)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/LeituraRodas.msg"
  DEPENDENCIES std_msgs builtin_interfaces
)

# O módulo tem nome distinto do pacote gerado por ROSIDL.
ament_get_python_install_dir(PYTHON_INSTALL_DIR)
install(DIRECTORY simulador_base_nos
  DESTINATION ${PYTHON_INSTALL_DIR}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
)
install(PROGRAMS programas/simular DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(testes_simulador_base testes
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    APPEND_ENV PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}
    TIMEOUT 60
  )
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
