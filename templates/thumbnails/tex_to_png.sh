#!/bin/bash

# Calling Example: sh tex_to_png.sh asamblea_thumbnail 123 "El Amor de Dios"

TemplateName=$1
IdNumber=$2
ThemeText=$3
SearchString="s/%\\\\uppercase{}/\\\\uppercase{${ThemeText}}/g"

#echo $TemplateName
#echo $SearchString

cp "${TemplateName}.tex" "${TemplateName}_id_${IdNumber}.tex";
cp "${TemplateName}.aux" "${TemplateName}_id_${IdNumber}.aux";
sed -i "${SearchString}" "${TemplateName}_id_${IdNumber}.tex";
xelatex "${TemplateName}_id_${IdNumber}.tex";
pdftoppm "${TemplateName}_id_${IdNumber}.pdf" "${TemplateName}_id_${IdNumber}" -png -singlefile -r 72;
rm "${TemplateName}_id_${IdNumber}.pdf";
rm "${TemplateName}_id_${IdNumber}.log";
rm "${TemplateName}_id_${IdNumber}.aux";
rm "${TemplateName}_id_${IdNumber}.tex";

