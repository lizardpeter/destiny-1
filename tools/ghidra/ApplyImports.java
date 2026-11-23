// Post-analysis: name the import slots and their jump stubs from imports.tsv (tools/ghidra/imports.py).
// Args: <imports.tsv>
//
// Each row's slot gets the label __imp_<name>. A function whose first instruction is a jump through a
// labelled slot is that import's stub and takes the import's name, so its callers read as calls to the import.
// Imports whose NID has no known name are called nid_<NID>.
//@category D1
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;

public class ApplyImports extends GhidraScript {
	@Override
	public void run() throws Exception {
		Map<Address, String> slots = new HashMap<>();
		boolean header = true;
		for (String line : Files.readAllLines(Paths.get(getScriptArgs()[0]))) {
			if (header) {
				header = false;
				continue;
			}
			String[] c = line.split("\t", -1);
			if (c.length < 5) {
				continue;
			}
			String name = c[4].isEmpty() ? "nid_" + c[2].replaceAll("[^A-Za-z0-9]", "_") : c[4];
			Address a = toAddr(Long.parseLong(c[0], 16));
			slots.put(a, name);
			createLabel(a, "__imp_" + name, true, SourceType.IMPORTED);
		}
		int stubs = 0;
		FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
		while (it.hasNext()) {
			Function f = it.next();
			Instruction ins = getInstructionAt(f.getEntryPoint());
			if (ins == null || !ins.getMnemonicString().equals("JMP")) {
				continue;
			}
			for (Reference r : ins.getReferencesFrom()) {
				String name = slots.get(r.getToAddress());
				if (name != null) {
					f.setName(name, SourceType.IMPORTED);
					stubs++;
					break;
				}
			}
		}
		println(String.format("imports: %d slots labelled, %d stubs named", slots.size(), stubs));
	}
}
