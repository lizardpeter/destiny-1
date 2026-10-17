
void FUN_0058dc90(undefined8 param_1,char *param_2)

{
  char cVar1;
  long *plVar2;
  char cVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  long lVar6;
  char local_1a1;
  undefined **local_1a0 [3];
  undefined4 local_188;
  undefined4 local_e4;
  long local_38;
  
  plVar2 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  uVar5 = FUN_0056b260();
  if (*(long *)(param_2 + 8) != 0) {
    uVar4 = FUN_00001df0(uVar5);
    lVar6 = FUN_0056dc00(uVar5,0,uVar4,param_2 + 8);
    if (lVar6 != 0) {
      uVar5 = FUN_0056b260();
      if (*(long *)(lVar6 + 8) != 0) {
        uVar4 = FUN_01009850(uVar5);
        lVar6 = FUN_0056dc00(uVar5,0,uVar4,lVar6 + 8);
        if (lVar6 != 0) {
          local_1a0[0] = &PTR_FUN_0193f210;
          local_188 = 0;
          local_e4 = 0;
          FUN_00556c70(0,lVar6 + 0x30,local_1a0,&local_1a1);
          cVar3 = '\x02';
          if (local_1a1 == '\0') {
            cVar3 = '\x03';
          }
          cVar1 = *param_2;
          if (*param_2 != cVar3) {
            *param_2 = cVar3;
            cVar1 = cVar3;
          }
          if (cVar1 == '\x03') {
            cVar3 = FUN_0058e4a0();
            if ((cVar3 != '\0') && (*param_2 != '\x04')) {
              *param_2 = '\x04';
            }
          }
          goto LAB_0058ddb4;
        }
      }
    }
  }
  if (*param_2 != '\x01') {
    *param_2 = '\x01';
  }
LAB_0058ddb4:
  if (*plVar2 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

