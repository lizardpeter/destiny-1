
void FUN_007de640(long param_1,uint param_2)

{
  float fVar1;
  float fVar2;
  undefined1 auVar3 [16];
  uint uVar4;
  
  if ((*(uint *)(param_1 + 0x25bc) != param_2) && (*(long *)(param_1 + 0x50) != 0)) {
    fVar1 = *(float *)(&DAT_015d2428 + (ulong)param_2 * 0xc);
    fVar2 = *(float *)(&DAT_015d2424 + (ulong)param_2 * 0xc) +
            *(float *)(&DAT_015d2424 + (ulong)param_2 * 0xc);
    auVar3 = vcmpss_avx(ZEXT416((uint)fVar2),ZEXT816(0),4);
    uVar4 = auVar3._0_4_ & 1;
    FUN_00f81ad0(param_1 + 0x25d4,uVar4,uVar4);
    FUN_00f80790(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(FUN_000025d0 + param_1 + 4));
    fVar1 = fVar1 * DAT_0165fe78;
    FUN_00f808a0(fVar1,fVar2,*(undefined8 *)(param_1 + 0x50));
    FUN_00f80910(fVar1,fVar2,*(undefined8 *)(param_1 + 0x50));
    FUN_00f80830(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(&DAT_000025ac + param_1));
    *(uint *)(param_1 + 0x25bc) = param_2;
  }
  return;
}

