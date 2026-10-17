  BEGIN { FS=":" }
  NR != 1 { exit 1 }
  NF < 1 || NF > 2 { exit 1 }
  {
    host=tolower($1); port=443;
    if (length(host)>253 || host !~ /^[a-z0-9.-]+$/) exit 1;
    count=split(host,labels,".");
    for (i=1;i<=count;i++) if (length(labels[i])<1 || length(labels[i])>63 || labels[i] !~ /^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/) exit 1;
    if (NF==2) { if ($2 !~ /^[0-9]+$/ || length($2)>5 || $2+0<1 || $2+0>65535) exit 1; port=$2+0; }
    if (port==443) printf "%s",host; else printf "%s:%d",host,port;
  }
  END { if (NR != 1) exit 1 }
