
void FUN_0090e360(void)

{
  int iVar1;
  long lVar2;
  long lVar3;
  undefined8 *puVar4;
  undefined8 *puVar5;
  byte bVar6;
  undefined1 local_170 [8];
  undefined4 local_168;
  undefined8 local_160;
  undefined4 uStack_158;
  undefined4 uStack_154;
  undefined4 uStack_150;
  undefined4 uStack_14c;
  undefined8 uStack_148;
  undefined8 local_140;
  undefined8 uStack_138;
  undefined8 uStack_130;
  undefined8 uStack_128;
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 uStack_110;
  undefined8 uStack_108;
  undefined8 local_100;
  undefined8 uStack_f8;
  undefined8 uStack_f0;
  undefined8 uStack_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 uStack_d0;
  undefined8 uStack_c8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined8 local_90;
  undefined8 local_88;
  undefined8 local_80;
  long local_60;
  
  bVar6 = 0;
  local_60 = *DAT_01a1f100;
  FUN_00074a80(local_170,DAT_0273ea80);
  lVar2 = FUN_00074a90(local_170);
  if (lVar2 != 0) {
    do {
      if ((*(byte *)(lVar2 + 0x610) & 2) == 0) {
        local_c0 = 0;
        uStack_b0 = 0;
        uStack_a8 = 0;
        local_e0 = 0;
        uStack_d8 = 0;
        uStack_d0 = 0;
        uStack_c8 = 0;
        local_100 = 0;
        uStack_f8 = 0;
        uStack_f0 = 0;
        uStack_e8 = 0;
        local_120 = 0;
        uStack_118 = 0;
        uStack_110 = 0;
        uStack_108 = 0;
        uStack_130 = 0;
        uStack_128 = 0;
        uStack_14c = 0;
        uStack_154 = (undefined4)*(undefined8 *)(lVar2 + 0x620);
        uStack_150 = (undefined4)((ulong)*(undefined8 *)(lVar2 + 0x620) >> 0x20);
        local_160 = (ulong)CONCAT12(*(undefined1 *)(lVar2 + 0x62c),1);
        uStack_158 = *(undefined4 *)(lVar2 + 0x630);
        uStack_138 = *(undefined8 *)(lVar2 + 0x614);
        local_140 = *(undefined8 *)
                     ((ulong)((*(uint *)(lVar2 + 4) & 0x1fff) * DAT_02689590) + 0x30 + DAT_02689588)
        ;
        uStack_148 = *(undefined8 *)(lVar2 + 0x638);
        puVar4 = (undefined8 *)(lVar2 + 0x760);
        puVar5 = &uStack_130;
        for (lVar3 = 0xf; lVar3 != 0; lVar3 = lVar3 + -1) {
          *puVar5 = *puVar4;
          puVar4 = puVar4 + (ulong)bVar6 * -2 + 1;
          puVar5 = puVar5 + (ulong)bVar6 * -2 + 1;
        }
        uStack_b8 = *(undefined8 *)(lVar2 + 0x7d8);
        uStack_b0 = CONCAT35(uStack_b0._5_3_,*(undefined5 *)(lVar2 + 0x7e0));
        uStack_a8 = CONCAT44(uStack_a8._4_4_,*(undefined4 *)(lVar2 + 0x7e8));
        local_80 = *(undefined8 *)(lVar2 + 0x810);
        local_88 = *(undefined8 *)(lVar2 + 0x808);
        local_90 = *(undefined8 *)(lVar2 + 0x800);
        local_a0 = *(undefined8 *)(lVar2 + 0x7f0);
        local_98 = *(undefined8 *)(lVar2 + 0x7f8);
        FUN_0090e5a0(local_168,0);
        FUN_0090e840(local_168,&local_160,0);
      }
      iVar1 = FUN_00071f60(lVar2 + 0x688);
      if ((iVar1 != -1) && (*(int *)(lVar2 + 0x690) != -1)) {
        FUN_00649330(local_168);
      }
      *(byte *)(lVar2 + 0x14) = *(byte *)(lVar2 + 0x14) | 1;
      lVar2 = FUN_00074a90(local_170);
    } while (lVar2 != 0);
  }
  if (*DAT_01a1f100 == local_60) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

