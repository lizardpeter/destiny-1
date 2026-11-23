// Pre-analysis: create a function at every start the unwind table lists (unwind.tsv from tools/ghidra/unwind.py),
// so auto-analysis covers functions nothing calls directly (virtual methods, callbacks).
// Args: <unwind.tsv>
//@category D1
import java.nio.file.Files;
import java.nio.file.Paths;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;

public class CreateUnwindFunctions extends GhidraScript {
	@Override
	public void run() throws Exception {
		int listed = 0, made = 0, failed = 0;
		boolean header = true;
		for (String line : Files.readAllLines(Paths.get(getScriptArgs()[0]))) {
			if (header) {
				header = false;
				continue;
			}
			String[] c = line.split("\t", -1);
			if (c[0].isEmpty()) {
				continue;
			}
			monitor.checkCancelled();
			listed++;
			Address a = toAddr(Long.parseLong(c[0], 16));
			if (getFunctionAt(a) != null) {
				continue;
			}
			if (getInstructionAt(a) == null) {
				disassemble(a);
			}
			if (getInstructionAt(a) != null && createFunction(a, null) != null) {
				made++;
			}
			else {
				failed++;
				if (failed <= 20) {
					printerr("could not create a function at " + a);
				}
			}
		}
		println(String.format("unwind: %d listed, %d functions created, %d failed", listed, made, failed));
	}
}
