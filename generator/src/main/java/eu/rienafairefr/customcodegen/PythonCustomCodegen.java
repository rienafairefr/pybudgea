package eu.rienafairefr.customcodegen;

import io.swagger.v3.oas.models.media.ArraySchema;
import io.swagger.v3.oas.models.media.Schema;
import org.apache.commons.lang3.StringUtils;
import org.openapitools.codegen.SupportingFile;
import org.openapitools.codegen.languages.PythonClientCodegen;
import org.openapitools.codegen.utils.ModelUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.openapitools.codegen.utils.StringUtils.underscore;

public class PythonCustomCodegen extends PythonClientCodegen {
    private static final Logger LOGGER = LoggerFactory.getLogger(PythonCustomCodegen.class);

    @Override
    public void processOpts() {
        super.processOpts();

        supportingFiles.add(new SupportingFile("schema_fields.mustache", packagePath(), "fields.py"));
    }

    @Override
    public String toExampleValue(Schema schema) {
        return toExampleValueRecursive(schema, new ArrayList<String>(), 5);
    }

    private String toExampleValueRecursive(Schema schema, List<String> included_schemas, int indentation) {
        String indentation_string = "";
        for (int i=0 ; i< indentation ; i++) indentation_string += "    ";
        String example = super.toExampleValue(schema);

        // correct "true"s into "True"s, since super.toExampleValue uses "toString()" on Java booleans
        if (ModelUtils.isBooleanSchema(schema) && null!=example) {
            if ("false".equalsIgnoreCase(example)) example = "False";
            else example = "True";
        }

        // correct "&#39;"s into "'"s after toString()
        if (ModelUtils.isStringSchema(schema) && schema.getDefault() != null) {
            example = (String) schema.getDefault();
        }

        Schema refSchema = null;

        if (null != schema.get$ref()) {
            // $ref case:
            Map<String, Schema> allDefinitions = ModelUtils.getSchemas(this.openAPI);
            String ref = ModelUtils.getSimpleRef(schema.get$ref());
            if (allDefinitions != null) {
                refSchema = allDefinitions.get(ref);
            } else {
                LOGGER.warn("allDefinitions not defined in toExampleValue!\n");
            }
        }

        if (schema.getEnum() != null && !schema.getEnum().isEmpty()) {
            // Enum case:
            example = schema.getEnum().get(0).toString();
            if (ModelUtils.isStringSchema(schema)) {
                example = "'" + escapeText(example) + "'";
            }
            if (null == example)
                LOGGER.warn("Empty enum. Cannot built an example!");

            return example;
        } else if (null != schema.get$ref()) {
            // $ref case:
            String ref = ModelUtils.getSimpleRef(schema.get$ref());
            if (null == refSchema) {
                return "None";
            } else {
                String refTitle = refSchema.getTitle();
                if (StringUtils.isBlank(refTitle) || "null".equals(refTitle)) {
                    refSchema.setTitle(ref);
                }
                if (StringUtils.isNotBlank(schema.getTitle()) && !"null".equals(schema.getTitle())) {
                    included_schemas.add(schema.getTitle());
                }
                return toExampleValueRecursive(refSchema, included_schemas, indentation);
            }
        }
        if (ModelUtils.isDateSchema(schema)) {
            example = "datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date()";
            return example;
        } else if (ModelUtils.isDateTimeSchema(schema)) {
            example = "datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f')";
            return example;
        } else if (ModelUtils.isBinarySchema(schema)) {
            example = "bytes(b'blah')";
            return example;
        } else if (ModelUtils.isByteArraySchema(schema)) {
            example = "YQ==";
        } else if (ModelUtils.isStringSchema(schema)) {
            // a BigDecimal:
            if ("Number".equalsIgnoreCase(schema.getFormat())) {return "1";}
            if (StringUtils.isNotBlank(schema.getPattern())) return "'a'"; // I cheat here, since it would be too complicated to generate a string from a regexp
            int len = 0;
            if (null != schema.getMinLength()) len = schema.getMinLength().intValue();
            if (len < 1) len = 1;
            example = "";
            for (int i=0;i<len;i++) example += i;
        } else if (ModelUtils.isIntegerSchema(schema)) {
            if (schema.getMinimum() != null)
                example = schema.getMinimum().toString();
            else
                example = "56";
        } else if (ModelUtils.isNumberSchema(schema)) {
            if (schema.getMinimum() != null)
                example = schema.getMinimum().toString();
            else
                example = "1.337";
        } else if (ModelUtils.isBooleanSchema(schema)) {
            example = "True";
        } else if (ModelUtils.isArraySchema(schema)) {
            if (StringUtils.isNotBlank(schema.getTitle()) && !"null".equals(schema.getTitle())) {
                included_schemas.add(schema.getTitle());
            }
            ArraySchema arrayschema = (ArraySchema) schema;
            example = "[\n" + indentation_string + toExampleValueRecursive(arrayschema.getItems(), included_schemas, indentation+1) + "\n" + indentation_string + "]";
        } else if (ModelUtils.isMapSchema(schema)) {
            if (StringUtils.isNotBlank(schema.getTitle()) && !"null".equals(schema.getTitle())) {
                included_schemas.add(schema.getTitle());
            }
            Object additionalObject = schema.getAdditionalProperties();
            if (additionalObject instanceof Schema) {
                Schema additional = (Schema) additionalObject;
                String the_key = "'key'";
                if (additional.getEnum() != null && !additional.getEnum().isEmpty()) {
                    the_key = additional.getEnum().get(0).toString();
                    if (ModelUtils.isStringSchema(additional)) {
                        the_key = "'" + escapeText(the_key) + "'";
                    }
                }
                example = "{\n" + indentation_string + the_key + " : " + toExampleValueRecursive(additional, included_schemas, indentation+1) + "\n" + indentation_string + "}";
            } else {
                example = "{ }";
            }
        } else if (ModelUtils.isObjectSchema(schema)) {
            if (StringUtils.isBlank(schema.getTitle())) {
                example = "None";
                return example;
            }

            // I remove any property that is a discriminator, since it is not well supported by the python generator
            String toExclude = null;
            if (schema.getDiscriminator()!=null) {
                toExclude = schema.getDiscriminator().getPropertyName();
            }

            example = packageName + ".models." + underscore(schema.getTitle())+"."+schema.getTitle()+"(";

            // if required only:
            // List<String> reqs = schema.getRequired();

            // if required and optionals
            List<String> reqs = new ArrayList<>();
            if (schema.getProperties() != null && !schema.getProperties().isEmpty()) {
                for (Object toAdd : schema.getProperties().keySet()) {
                    reqs.add((String) toAdd);
                }

                Map<String, Schema> properties = schema.getProperties();
                Set<String> propkeys = null;
                if (properties != null) propkeys = properties.keySet();
                if (toExclude != null && reqs.contains(toExclude)) {
                    reqs.remove(toExclude);
                }
                for (String toRemove : included_schemas) {
                    if (reqs.contains(toRemove)) {
                        reqs.remove(toRemove);
                    }
                }
                if (StringUtils.isNotBlank(schema.getTitle()) && !"null".equals(schema.getTitle())) {
                    included_schemas.add(schema.getTitle());
                }
                if (null != schema.getRequired()) for (Object toAdd : schema.getRequired()) {
                    reqs.add((String) toAdd);
                }
                if (null != propkeys) for (String propname : propkeys) {
                    Schema schema2 = properties.get(propname);
                    if (reqs.contains(propname)) {
                        String refTitle = schema2.getTitle();
                        if (StringUtils.isBlank(refTitle) || "null".equals(refTitle)) {
                            schema2.setTitle(propname);
                        }
                        example += "\n" + indentation_string + underscore(propname) + " = " +
                                toExampleValueRecursive(schema2, included_schemas, indentation + 1) + ", ";
                    }
                }
            }
            example +=")";
        } else {
            LOGGER.warn("Type " + schema.getType() + " not handled properly in toExampleValue");
        }

        if (ModelUtils.isStringSchema(schema)) {
            example = "'" + escapeText(example) + "'";
        }

        return example;
    }
}
