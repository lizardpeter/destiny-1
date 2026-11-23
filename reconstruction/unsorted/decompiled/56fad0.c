
void FUN_0056fad0(int *param_1,int *param_2,long param_3)

{
  char cVar1;
  long *plVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  undefined1 auVar6 [16];
  int local_38;
  int local_34;
  long local_30;
  
  plVar2 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  if ((((short)param_2[3] != -1) && ((short)param_1[3] != -1)) && (0 < *param_2 - *param_1)) {
    FUN_00ac15f0(param_2,*param_2 - *param_1,param_3);
    uVar4 = FUN_002749e0((short)param_1[3]);
    FUN_00274af0(uVar4,*param_1,&local_34,0,0,&local_38);
    iVar3 = FUN_00274e30(param_2);
    if (local_34 < iVar3) {
      uVar4 = FUN_005494c0();
      auVar6 = FUN_0054bba0(uVar4,(short)param_2[3]);
      lVar5 = auVar6._8_8_;
      if ((auVar6._0_8_ != 0) && (lVar5 != 0)) {
        cVar1 = *(char *)((long)local_38 * 0x20 + lVar5 + 0x48 + *(long *)(lVar5 + 0x30));
        if (cVar1 == '\x02') {
          if (param_3 != 0) {
            FUN_00ac16f0(param_3,param_2);
          }
        }
        else if (cVar1 == '\x01') {
          FUN_00ac1640(param_2);
          FUN_0091a100();
        }
      }
    }
  }
  if (*plVar2 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

