FROM jimschubert/8-jdk-alpine-mvn:1.0 as build

COPY pom.xml .

RUN mvn dependency:go-offline

COPY src /src

RUN mvn package

FROM openapitools/openapi-generator-cli:v4.2.3

COPY --from=build /target/customcodegen-openapi-generator-1.0.0.jar customcodegen.jar

ENTRYPOINT ["java", "-cp", \
"customcodegen.jar:/opt/openapi-generator/modules/openapi-generator-cli/target/openapi-generator-cli.jar", \
"org.openapitools.codegen.OpenAPIGenerator"]