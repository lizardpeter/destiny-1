// Decompile prioritized exact RMGE01 functions from the owner-provided DOL.
//@category SuperMarioGalaxy

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class SMGExportUnmatchedSlices extends GhidraScript {
    private static class Row {
        String address;
        long size;
        String name;
        Row(String address, long size, String name) {
            this.address = address;
            this.size = size;
            this.name = name;
        }
    }

    private static String j(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder();
        b.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '\\': b.append("\\\\"); break;
                case '"': b.append("\\\""); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int)c));
                    else b.append(c);
            }
        }
        b.append('"');
        return b.toString();
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException("usage: SMGExportUnmatchedSlices.java <frontier.tsv> <out.json> [max]");
        }
        Path frontierPath = Path.of(args[0]);
        Path outPath = Path.of(args[1]);
        int max = args.length >= 3 ? Integer.parseInt(args[2]) : 128;

        List<Row> rows = new ArrayList<>();
        for (String line : Files.readAllLines(frontierPath, StandardCharsets.UTF_8)) {
            if (line.isBlank() || line.startsWith("#")) continue;
            String[] p = line.split("\\t", 3);
            if (p.length < 3) continue;
            rows.add(new Row(p[0], Long.parseLong(p[1]), p[2]));
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("failed to initialize decompiler");
        }

        StringBuilder out = new StringBuilder();
        out.append("{\n");
        out.append("  \"schema\": \"smg_rmge01_ghidra_unmatched_slices/v1\",\n");
        out.append("  \"program\": {");
        out.append("\"name\":").append(j(currentProgram.getName())).append(",");
        out.append("\"executable_sha256\":").append(j(currentProgram.getExecutableSHA256())).append(",");
        out.append("\"language_id\":").append(j(currentProgram.getLanguageID().toString()));
        out.append("},\n");
        out.append("  \"functions\": [\n");

        int exported = 0;
        int missing = 0;
        boolean firstRecord = true;
        int limit = Math.min(max, rows.size());

        for (int ri = 0; ri < limit; ri++) {
            if (monitor.isCancelled()) break;
            Row row = rows.get(ri);
            Address address;
            try {
                address = toAddr(row.address);
            }
            catch (Exception e) {
                missing++;
                continue;
            }

            Function function = fm.getFunctionAt(address);
            if (function == null) {
                try { disassemble(address); } catch (Exception ignored) {}
                function = fm.getFunctionAt(address);
            }
            if (function == null) {
                try { function = createFunction(address, row.name); } catch (Exception ignored) {}
            }
            if (function == null) {
                function = fm.getFunctionContaining(address);
            }
            if (function == null) {
                missing++;
                continue;
            }

            int instructionCount = 0;
            List<String> calls = new ArrayList<>();
            InstructionIterator it = listing.getInstructions(function.getBody(), true);
            while (it.hasNext()) {
                Instruction ins = it.next();
                instructionCount++;
                for (Reference ref : ins.getReferencesFrom()) {
                    if (!ref.getReferenceType().isCall()) continue;
                    Address target = ref.getToAddress();
                    Function owner = target == null ? null : fm.getFunctionContaining(target);
                    String call = (target == null ? "" : target.toString()) + "|" +
                        (owner == null ? "" : owner.getName());
                    calls.add(call);
                }
            }

            String cText = null;
            String decError = null;
            boolean completed = false;
            try {
                DecompileResults result = decompiler.decompileFunction(function, 120, monitor);
                completed = result.decompileCompleted();
                if (completed && result.getDecompiledFunction() != null) {
                    cText = result.getDecompiledFunction().getC();
                }
                else {
                    decError = result.getErrorMessage();
                }
            }
            catch (Exception e) {
                decError = e.toString();
            }

            if (!firstRecord) out.append(",\n");
            firstRecord = false;
            out.append("    {");
            out.append("\"frontier_address\":").append(j(row.address)).append(",");
            out.append("\"frontier_size\":").append(row.size).append(",");
            out.append("\"frontier_name\":").append(j(row.name)).append(",");
            out.append("\"entry\":").append(j(function.getEntryPoint().toString())).append(",");
            out.append("\"ghidra_name\":").append(j(function.getName())).append(",");
            out.append("\"prototype\":").append(j(function.getPrototypeString(false, true))).append(",");
            out.append("\"instruction_count\":").append(instructionCount).append(",");
            out.append("\"decompile_completed\":").append(completed).append(",");
            out.append("\"decompile_error\":").append(j(decError)).append(",");
            out.append("\"c\":").append(j(cText)).append(",");
            out.append("\"calls\":[");
            for (int i = 0; i < calls.size(); i++) {
                if (i != 0) out.append(",");
                out.append(j(calls.get(i)));
            }
            out.append("]}");
            exported++;
        }

        out.append("\n  ],\n");
        out.append("  \"requested\": ").append(limit).append(",\n");
        out.append("  \"exported\": ").append(exported).append(",\n");
        out.append("  \"missing\": ").append(missing).append("\n");
        out.append("}\n");

        Files.writeString(outPath, out.toString(), StandardCharsets.UTF_8);
        println("SMG RMGE01 Ghidra export: " + exported + " exported, " + missing + " missing");
    }
}
