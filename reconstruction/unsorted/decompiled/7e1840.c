
void FUN_007e1840(undefined8 *param_1,uint param_2,ulong param_3,int param_4)

{
  long lVar1;
  long lVar2;
  
  switch((ulong)param_2) {
  case 0:
    break;
  case 1:
    param_4 = param_4 * 2;
    break;
  case 2:
    param_4 = param_4 + 1;
    break;
  case 3:
  case 6:
    param_4 = param_4 * 3;
    break;
  case 4:
  case 5:
    param_4 = param_4 + 2;
    break;
  case 7:
    param_4 = param_4 << 2;
    break;
  default:
    param_4 = 0;
  }
  lVar2 = (param_3 & 0xffffffff) * 2 + *(long *)*param_1;
  FUN_00f7f1e0(param_1[10],*(undefined4 *)(&DAT_015d13c0 + (ulong)param_2 * 4));
  FUN_00f7f790(param_1[10],0);
  FUN_00f80730(param_1[10],0xffff);
  FUN_00f7f840(param_1[10],param_4);
  FUN_00f7f7e0(param_1[10],lVar2);
  lVar1 = param_1[10];
  FUN_00f8df60(lVar1 + 0xc0,lVar1,lVar1 + 0x80);
  FUN_00f7f320(lVar1,param_4,lVar2);
  FUN_00f8e880(lVar1 + 0xc0,lVar1,lVar1 + 0x80);
  return;
}

