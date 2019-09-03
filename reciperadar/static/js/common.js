function float2rat(x) {
    var tolerance = 1.0E-2;
    var h1=1; var h2=0;
    var k1=0; var k2=1;
    var b = x;
    do {
        var a = Math.floor(b);
        var aux = h1; h1 = a*h1+h2; h2 = aux;
        aux = k1; k1 = a*k1+k2; k2 = aux;
        b = 1/(b-a);
    } while (Math.abs(x-h1/k1) > x*tolerance);

    if (k1 === 1) return h1;
    if (h1 > k1) {
        h1 = Math.floor(h1 / k1);
        return h1+" 1/"+k1;
    }
    return h1+"/"+k1;
}
