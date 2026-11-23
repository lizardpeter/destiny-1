
void FUN_00302a60(uint param_1)

{
  long lVar1;
  uint *puVar2;
  uint uVar3;
  ulong uVar4;
  
  puVar2 = DAT_02689600;
  lVar1 = DAT_02689588;
  uVar4 = (ulong)(DAT_02689590 * (param_1 & 0x1fff));
  FUN_002e36f0(DAT_02689588 + uVar4);
  FUN_0006ecb0(&DAT_02689580,param_1);
  uVar3 = ~(1 << ((byte)(param_1 & 0x1fff) & 0x1f));
  *puVar2 = *puVar2 & uVar3;
  puVar2[1] = puVar2[1] & uVar3;
  puVar2[0x2a] = puVar2[0x2a] + 1;
  FUN_001195f0(lVar1 + 0x18 + uVar4);
  return;
}

