# D1 Tower nested NPC/enemy/AI carrier breakthrough — 2026-09-06

## Why the prior A–G census was incomplete

The source-owned Tower Activity reconstruction currently contains 1,215 unique runtime WorldIDs and 162 placed SEntity owners.  The A–G articulated pass is only the subset whose directly placed SEntities expose model+skeleton evidence through the ordinary world-placement path.

That is not the complete Tower actor population.

Charm's pinned D1 implementation contains a second, explicit path inside `Activity.CollapseResourceParent`:

```csharp
// For NPCs, enemies and other AI
// if (b.Unk00.TagData.EntityResource.TagData.Unk10.GetValue(...) is SBC078080 c)
// {
//     var d = (SA7058080)b.Unk00.TagData.EntityResource.TagData.Unk18.GetValue(...);
//     if (!items.Contains(d.Unk68.Hash))
//         items.Add(d.Unk68.Hash);
// }
```

Pinned source:

- `MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af`
- `Tiger/Schema/Activity/Activity.cs`
- `Tiger/Schema/Activity/ActivityStructsROI.cs`

The exact D1 classes are:

```text
SBC078080  = 808007BC
SA7058080  = 808005A7
SD9128080  = 808012D9
```

and `SA7058080 +0x68` is `Tag<SD9128080>`.

Therefore this path is source-level semantic evidence for a broad **NPC/enemy/other-AI carrier** class.  It is not an appearance inference.

## Concrete Tower evidence

The current full Activity/F603 corpus contains:

```text
F603 EntityResource sources                 855
SBC078080 -> SA7058080 class-pair carriers  144
```

Activity ownership of those 144 carriers is scenario-dependent because many carriers are shared between Tower scenario variants.  The exact current counts by activity reference are:

```text
city_tower_default1:scenario_client   49
city_tower_queen:scenario_client      50
city_tower_harvest:scenario_client    50
city_tower_srl:scenario_client        49
city_tower_fol:scenario_client        49
city_tower_crimson:scenario_client    49
city_tower_chalice:scenario_client    49
ambient_city_tower:scenario_client    49
```

Within the ambient Tower activity specifically, 28 SBC07/A705 carriers are unique to `ambient_city_tower:scenario_client`; another 21 are shared with one or more scenario activities, for **49 ambient-referenced AI carriers total**.

This is the first direct explanation for why the r10 A–G export visibly under-populates the Tower: the direct model+skeleton placement census deliberately did not follow the separate AI carrier path.

## Sweeper / broom consequence

The broom-shaped direct object is already source-closed as:

```text
WorldID      1A02E90A214E971E
SEntity      80C7A532
EntityModel  80CA0D19
translation  [127.732521, 93.543388, -9.023452]
```

A fresh 5 m spatial census found no other directly placed actor beside that broom.  This is now consistent with the source architecture: the sweeper body can be spawned through the nested SBC07 -> A705 -> D912 AI path while the broom exists as an independently serialized world object.  The old direct-placement-only proximity test therefore could not see the sweeper actor.

No attachment is yet claimed.  The remaining proof is to recover the exact spawned actor record near the broom and then locate the serialized hand/socket/prop relationship.

## Parser correction

The first scripted identity census searched for top-level tags whose file-entry Reference was `808005A7`.  That produced `current_a705_count = 0` and missed this path.

That was the wrong ownership model for Tower AI.  Charm shows that `SA7058080` is a **nested ResourcePointer payload inside an EntityResource's Unk18**, not necessarily a top-level `808005A7` file entry.

The new implementation follows the correct chain directly from each F603-owned EntityResource:

```text
SF6038080
  -> EntityResource
     Unk10 ResourcePointer class == 808007BC
     Unk18 ResourcePointer class == 808005A7
       nested SA705 +0x68
         -> SD9128080 FileHash
           -> scripted spawn groups / SMapDataEntry records
             -> spawned EntitySK
```

New durable implementation:

- `tools/d1_tower_ai_spawner_census.py`
- `.github/workflows/d1-tower-ai-spawner-census.yml`

Commits:

```text
b27e9ac1737e6ac5a7be4ae0a0ca1567e5c2376e  trace nested AI spawners
246ea39c53817ec4434cc1b66308ff482e9d9a34  CI census
```

The workflow reopens the current retail Tower corpus, validates the exact SBC07/A705 pair, resolves every nested D912, parses its scripted spawn records, and classifies each spawned EntitySK through the same source-pinned SEntity model/skeleton dependency parser used by the A–G census.

## Current proof boundary

Safe to claim now:

- r10's A–G direct articulated set is not the full actor population.
- Tower data contains 144 exact Charm-classified NPC/enemy/other-AI carriers.
- `ambient_city_tower` references 49 of those carriers.
- the prior direct-A705 search was structurally wrong for this path.
- the broom can coexist with a non-directly-placed spawned actor, which explains the missing nearby body in the old spatial census.

Not safe to claim yet:

- which spawned actor is specifically the sweeper;
- human/vendor names for every carrier;
- broom hand/socket ownership;
- exact startup/default animation for every spawned actor.

Those require the nested D912 census and subsequent actor/attachment joins.
