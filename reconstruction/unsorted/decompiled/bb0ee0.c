
void FUN_00bb0ee0(long param_1)

{
  long lVar1;
  char cVar2;
  uint uVar3;
  long lVar4;
  ulong uVar5;
  long lVar6;
  undefined1 local_1a0 [24];
  uint local_188;
  long local_180;
  undefined1 local_170 [8];
  undefined4 local_168 [2];
  undefined4 local_160;
  undefined4 local_158;
  undefined4 local_150;
  undefined4 local_148;
  undefined4 local_140;
  undefined4 local_138;
  undefined1 local_f8 [20];
  undefined4 local_e4;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_168[0] = 0x811c9dc5;
  local_160 = 0x811c9dc5;
  local_158 = 0x811c9dc5;
  local_150 = 0x811c9dc5;
  local_148 = 0x811c9dc5;
  local_140 = 0x811c9dc5;
  local_138 = 0x811c9dc5;
  local_e4 = 1;
  FUN_00072240(local_f8,*(undefined8 *)(param_1 + 8),*(undefined4 *)(param_1 + 4));
  FUN_00072400(local_f8);
  FUN_000730b0(local_f8,local_170,0x3a0);
  cVar2 = FUN_00072210(local_f8);
  FUN_00072650(local_f8);
  if (cVar2 == '\0') {
    uVar3 = FUN_00071f60(local_170);
    if (uVar3 != 0xffffffff) {
      lVar4 = (ulong)((uVar3 & 0x1fff) * DAT_02692230) + DAT_02692228;
      if (lVar4 != 0) {
        cVar2 = FUN_00337fe0(lVar4,*(undefined4 *)PTR_DAT_019b1b40,local_1a0,0);
        if (cVar2 != '\0') {
          lVar6 = (ulong)(((uint)((int)local_188 >> 0xd) >> 0x12 | 0x3ff) & (int)local_188 >> 0xd) *
                  0x40;
          lVar4 = *DAT_01a238a0;
          lVar1 = *(long *)(lVar4 + 0x10 + lVar6);
          uVar5 = (ulong)((local_188 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar6));
          uVar3 = *(uint *)(local_180 + 0x24 +
                           ((lVar1 + uVar5) -
                           ((long)*(int *)(lVar4 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar5))));
          if (uVar3 != 0xffffffff) {
            lVar6 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
            lVar1 = *(long *)(lVar4 + 0x10 + lVar6);
            uVar5 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar6));
            lVar4 = (lVar1 + uVar5) -
                    ((long)*(int *)(lVar4 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar5));
            if (lVar4 != 0) {
              FUN_00644640(lVar4,local_168);
            }
          }
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

