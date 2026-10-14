
uint FUN_00302640(uint param_1,undefined1 param_2,undefined4 param_3,long param_4)

{
  uint *puVar1;
  char cVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = DAT_02689600;
  cVar2 = FUN_0006eeb0(&DAT_02689580,param_1 & 0xffff);
  uVar3 = 0xffffffff;
  if (cVar2 == '\0') {
    uVar3 = FUN_0006ea80(&DAT_02689580,param_1 & 0xffff);
    FUN_00301470((ulong)((uVar3 & 0x1fff) * DAT_02689590) + DAT_02689588,param_4,param_2,param_1,
                 uVar3,param_3);
    uVar4 = 1 << ((byte)param_1 & 0x1f);
    *puVar1 = *puVar1 | uVar4;
    puVar1[1] = puVar1[1] | uVar4;
    puVar1[0x2a] = puVar1[0x2a] + 1;
    FUN_001195f0(param_4 + 0x10);
  }
  return uVar3;
}

