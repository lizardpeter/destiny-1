
void FUN_007dc7b0(long param_1)

{
  ulong uVar1;
  undefined4 uVar2;
  
  DAT_026df292 = FUN_00f848f0();
  uVar2 = FUN_00f83530(&DAT_026df294,0x100,0x100,1,1,0xfac00a,8,0,0);
  uVar1 = FUN_000b4a60(uVar2,0xe);
  thunk_FUN_012aa986(uVar1,0xff,uVar2);
  FUN_00f841b0(&DAT_026df294,uVar1 >> 8 & 0xffffffff);
  FUN_00f839a0(&DAT_026df294,0x10);
  uVar2 = FUN_00f83530(&DAT_026df2b4,0x100,0x100,1,1,0xfac00a,8,0,0);
  uVar1 = FUN_000b4a60(uVar2,0xe);
  thunk_FUN_012aa986(uVar1,0,uVar2);
  FUN_00f841b0(&DAT_026df2b4,uVar1 >> 8 & 0xffffffff);
  FUN_00f839a0(&DAT_026df2b4,0x10);
  FUN_00f82bd0(&DAT_026df2d4);
  FUN_00f82c00(&DAT_026df2d4,2);
  FUN_00f82d00(&DAT_026df2d4,1,1);
  FUN_00f82cb0(&DAT_026df2d4,6,6,6);
  FUN_00f82da0(&DAT_026df2d4,0,0);
  FUN_00f82d20(&DAT_026df2d4,4);
  FUN_00f81ee0(&DAT_026df2d4,0);
  FUN_00f82d40(&DAT_026df2d4,0);
  FUN_00f82c20(&DAT_026df2d4,0,0x7fffffff);
  *(undefined8 *)(param_1 + 0x27e4) = 0;
  *(undefined8 *)(param_1 + 0x27dc) = 0;
  *(undefined8 *)(FUN_000027d0 + param_1 + 4) = 0;
  *(undefined8 *)(&DAT_000027cc + param_1) = 0;
  *(undefined8 *)(&DAT_000027c4 + param_1) = 0;
  *(undefined8 *)(param_1 + 0x2800) = 0;
  *(undefined8 *)(param_1 + 0x2808) = 0;
  *(undefined8 *)(param_1 + 0x27f0) = 0;
  *(undefined8 *)(param_1 + 0x27f8) = 0;
  *(undefined8 *)(param_1 + 0x2820) = 0;
  *(undefined8 *)(param_1 + 0x2828) = 0;
  *(undefined8 *)(param_1 + 0x2810) = 0;
  *(undefined8 *)(param_1 + 0x2818) = 0;
  *(undefined8 *)(param_1 + 0x2838) = 0;
  *(undefined8 *)(param_1 + 0x2830) = 0;
  return;
}

