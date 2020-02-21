package eu.rienafairefr.customcodegen;

import org.openapitools.codegen.ClientOptInput;
import org.openapitools.codegen.DefaultGenerator;
import org.openapitools.codegen.config.CodegenConfigurator;

public class EntryPoint {
    public static void main(String[] args) {
        final CodegenConfigurator configurator = new CodegenConfigurator()
            .setGeneratorName("customcodegen") // use this codegen library
            .setPackageName("budgea")
            .setInputSpec(args[0])
            .setOutputDir(args[1]);

        final ClientOptInput clientOptInput = configurator.toClientOptInput();
        DefaultGenerator generator = new DefaultGenerator();
        generator.opts(clientOptInput).generate();
    }
}
