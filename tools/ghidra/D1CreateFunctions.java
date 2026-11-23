// Creates functions at the eh_frame start addresses listed (hex, one per line) in the file
// given as the script argument.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import java.nio.file.*;
import java.util.*;

public class D1CreateFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        List<String> lines = Files.readAllLines(Paths.get(getScriptArgs()[0]));
        int made = 0;
        for (String l : lines) {
            l = l.trim();
            if (l.isEmpty()) continue;
            Address a = toAddr(Long.parseLong(l, 16));
            if (getFunctionAt(a) == null) {
                disassemble(a);
                if (createFunction(a, null) != null) made++;
            }
        }
        println("D1CreateFunctions: created " + made + " of " + lines.size());
    }
}
