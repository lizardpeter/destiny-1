
void FUN_007de710(float param_1,float param_2,long param_3,char param_4)

{
  if (*(char *)(param_3 + 0x25c4) != param_4) {
    if ((*(float *)(&DAT_000025c8 + param_3) == param_1) &&
       (!NAN(*(float *)(&DAT_000025c8 + param_3)) && !NAN(param_1))) {
      if ((*(float *)(&DAT_000025cc + param_3) == param_2) &&
         (!NAN(*(float *)(&DAT_000025cc + param_3)) && !NAN(param_2))) {
        return;
      }
    }
    FUN_00f81dd0(param_3 + 0x25dc,param_4);
    FUN_00f7ea80(param_1,param_2,*(undefined8 *)(param_3 + 0x50));
    *(char *)(param_3 + 0x25c4) = param_4;
    *(float *)(&DAT_000025c8 + param_3) = param_1;
    *(float *)(&DAT_000025cc + param_3) = param_2;
  }
  return;
}

