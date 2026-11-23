
bool FUN_0055c050(undefined8 param_1,undefined8 param_2,char *param_3,char *param_4,
                 undefined8 param_5,undefined4 *param_6)

{
  char cVar1;
  
  *param_4 = *param_3;
  cVar1 = *param_3;
  if (cVar1 == '\x02') {
    thunk_FUN_012aa7c6(param_4 + 1,param_3 + 1,0x88);
    FUN_002a3620(param_4 + 1);
  }
  *param_6 = 0x89;
  return cVar1 == '\x02';
}

