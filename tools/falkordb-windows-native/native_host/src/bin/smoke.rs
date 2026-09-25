use falkordb_native_host::{Engine, NativeGraph};

fn require_row(out: &falkordb_native_host::QueryOutput, expected: &str) -> Result<(), String> {
    let found = out
        .rows
        .iter()
        .flatten()
        .any(|cell| cell == expected);
    if found {
        Ok(())
    } else {
        Err(format!("expected result cell {expected:?}, got {:?}", out.rows))
    }
}

fn main() -> Result<(), String> {
    let _engine = Engine::init()?;
    let graph = NativeGraph::new("windows-native-smoke");

    let out = graph.query("RETURN 1 AS value")?;
    require_row(&out, "Int(1)")?;

    let created = graph.query("CREATE (:WinNativeTest {x: 123})")?;
    if created.stats.nodes_created != 1 {
        return Err(format!(
            "CREATE expected nodes_created=1, got {}",
            created.stats.nodes_created
        ));
    }

    let out = graph.query("MATCH (n:WinNativeTest) RETURN n.x AS x")?;
    require_row(&out, "Int(123)")?;

    let created = graph.query("CREATE (:A)-[:R {w: 7}]->(:B)")?;
    if created.stats.nodes_created != 2 || created.stats.relationships_created != 1 {
        return Err(format!(
            "relationship CREATE stats wrong: nodes={}, rels={}",
            created.stats.nodes_created, created.stats.relationships_created
        ));
    }

    let out = graph.query("MATCH (:A)-[r:R]->(:B) RETURN r.w AS w")?;
    require_row(&out, "Int(7)")?;

    println!("NATIVE_SMOKE_OK");
    Ok(())
}
