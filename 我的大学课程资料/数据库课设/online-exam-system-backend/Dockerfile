FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app

RUN cat > /root/settings.xml <<'MAVEN_SETTINGS'
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
  <mirrors>
    <mirror>
      <id>huaweicloud</id>
      <mirrorOf>central</mirrorOf>
      <name>Huawei Cloud Maven</name>
      <url>https://mirrors.huaweicloud.com/repository/maven/</url>
    </mirror>
  </mirrors>
</settings>
MAVEN_SETTINGS

COPY pom.xml .
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -s /root/settings.xml clean package -DskipTests

FROM amazoncorretto:17-alpine
WORKDIR /app

RUN apk add --no-cache mariadb-client socat fontconfig ttf-dejavu

COPY --from=build /app/target/exam-1.0-SNAPSHOT.jar exam.jar
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]
