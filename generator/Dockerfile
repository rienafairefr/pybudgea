ARG OPENAPIGEN_VERSION
FROM jimschubert/8-jdk-alpine-mvn:1.0 as build

COPY pom.xml .

RUN mvn dependency:go-offline

COPY src /src

RUN mvn package

FROM openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION}

COPY --from=build /target/customcodegen-openapi-generator-1.0.0.jar customcodegen.jar

ENTRYPOINT ["java", "-cp", \
"customcodegen.jar:/opt/openapi-generator/modules/openapi-generator-cli/target/openapi-generator-cli.jar", \
"org.openapitools.codegen.OpenAPIGenerator"]