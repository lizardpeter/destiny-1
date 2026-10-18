
bool FUN_007ca770(void)

{
  int iVar1;
  long lVar2;
  
  iVar1 = FUN_007d3eb0(s_DDS___018e3600,DAT_015d2b28,0);
  DAT_026dd340 = iVar1;
  if (iVar1 != -1) {
    lVar2 = FUN_007e3a00(DAT_026e2be8);
    if (lVar2 != 0) {
      FUN_00f82bd0(&DAT_026dd344);
      FUN_00f82c00(&DAT_026dd344,2);
      FUN_00f82d00(&DAT_026dd344,1,1);
      FUN_00f82cb0(&DAT_026dd344,6,6,6);
      FUN_00f82da0(&DAT_026dd344,0,0);
      FUN_00f82d20(&DAT_026dd344,4);
      FUN_00f81ee0(&DAT_026dd344,0);
      FUN_00f82d40(&DAT_026dd344,0);
      FUN_00f82c20(&DAT_026dd344,0,0x7fffffff);
    }
  }
  return iVar1 != -1;
}

