import java.io.*;
import java.util.*;
import java.util.regex.*;

public class SimpleObfuscator {

    // Map for storing original names and their obfuscated counterparts
    private static Map<String, String> nameMap = new HashMap<>();
    private static int counter = 0;

    // Method to generate a new obfuscated name
    private static String getObfuscatedName(String originalName) {
        if (!nameMap.containsKey(originalName)) {
            nameMap.put(originalName, "obf" + counter++);
        }
        return nameMap.get(originalName);
    }

    // Method to obfuscate the content of a Java file
    public static String obfuscateCode(String code) {
        // Regex patterns to match classes, methods, and variables
        Pattern classPattern = Pattern.compile("\\bclass\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\b");
        Pattern methodPattern = Pattern.compile(
                "\\b(public|private|protected|static)?\\s*(void|int|double|float|String|boolean|char|long|short|byte)\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(");
        Pattern variablePattern = Pattern.compile("\\b([a-zA-Z_][a-zA-Z0-9_]*)\\b");

        // Obfuscate class names
        Matcher classMatcher = classPattern.matcher(code);
        while (classMatcher.find()) {
            String className = classMatcher.group(1);
            code = code.replaceAll("\\b" + Pattern.quote(className) + "\\b", getObfuscatedName(className));
        }

        // Obfuscate method names
        Matcher methodMatcher = methodPattern.matcher(code);
        while (methodMatcher.find()) {
            String methodName = methodMatcher.group(3);
            code = code.replaceAll("\\b" + Pattern.quote(methodName) + "\\b", getObfuscatedName(methodName));
        }

        // Obfuscate variable names (ignore already obfuscated variables)
        Matcher variableMatcher = variablePattern.matcher(code);
        while (variableMatcher.find()) {
            String variableName = variableMatcher.group(1);
            // Skip class and method names to avoid renaming them multiple times
            if (!nameMap.containsKey(variableName)) {
                code = code.replaceAll("\\b" + Pattern.quote(variableName) + "\\b", getObfuscatedName(variableName));
            }
        }

        return code;
    }

    // Method to read Java code from a file
    public static String readFile(String fileName) throws IOException {
        StringBuilder code = new StringBuilder();
        BufferedReader reader = new BufferedReader(new FileReader(fileName));
        String line;
        while ((line = reader.readLine()) != null) {
            code.append(line).append("\n");
        }
        reader.close();
        return code.toString();
    }

    // Method to write obfuscated Java code to a file
    public static void writeFile(String fileName, String code) throws IOException {
        BufferedWriter writer = new BufferedWriter(new FileWriter(fileName));
        writer.write(code);
        writer.close();
    }

    // Main method to run the obfuscator
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java SimpleObfuscator <inputFile> <outputFile>");
            return;
        }

        String inputFile = args[0];
        String outputFile = args[1];

        try {
            // Read the source Java file
            String code = readFile(inputFile);

            // Obfuscate the code
            String obfuscatedCode = obfuscateCode(code);

            // Write the obfuscated code to the output file
            writeFile(outputFile, obfuscatedCode);

            System.out.println("Obfuscation complete. Output written to: " + outputFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
