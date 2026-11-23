// Decompiles the functions containing the given hex addresses; writes C to <outdir>/<addr>.c.
// Args: outdir addr [addr...]
import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import java.nio.file.*;

public class D1Decompile extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Path out = Paths.get(args[0]);
        Files.createDirectories(out);
        DecompInterface d = new DecompInterface();
        d.openProgram(currentProgram);
        for (int i = 1; i < args.length; i++) {
            Function f = getFunctionContaining(toAddr(Long.parseLong(args[i], 16)));
            if (f == null) { println("no function at " + args[i]); continue; }
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            String c = r.decompileCompleted() ? r.getDecompiledFunction().getC() : ("// failed: " + r.getErrorMessage());
            Files.writeString(out.resolve(String.format("%x.c", f.getEntryPoint().getOffset())), c);
            println("decompiled " + f.getName());
        }
    }
}
