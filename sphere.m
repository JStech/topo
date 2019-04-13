function [tri, X, Y, Z, C] = sphere(I)
[h, w] = size(I);
X = zeros(h*w, 1);
Y = zeros(h*w, 1);
Z = zeros(h*w, 1);
C = zeros(h*w, 1);
tri = zeros((h-1)*(w-1)*2, 3);

for i=1:h
  for j=1:w
    [x, y, z] = sph2cart((j/w)*2*pi-pi, (i/h)*pi - pi/2, (double(I(i, j))+3e5)/4e4);
    C((i-1)*w+j) = double(I(i, j));
    X((i-1)*w+j) = x;
    Y((i-1)*w+j) = y;
    Z((i-1)*w+j) = z;
    if i<h && j<w
      a = (i-1)*w + j;
      b = (i-0)*w + j;
      c = (i-0)*w + j + 1;
      d = (i-1)*w + j + 1;
      tri(2*((i-1)*(w-1) + j)-1, :) = [a b c];
      tri(2*((i-1)*(w-1) + j),   :) = [a c d];
    end
  end
end
end
