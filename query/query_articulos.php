<?php
// api_articulos.php
header('Content-Type: application/json; charset=utf-8');
header("Access-Control-Allow-Origin: *");

// Conexión a la base de datos
$conexion = new mysqli('localhost', 'root', '', 'miguelhogar');
if ($conexion->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Error de conexión a la base de datos"]);
    exit;
}

// Parámetro de búsqueda (si existe)
$q = isset($_GET['q']) ? $conexion->real_escape_string($_GET['q']) : '';

// Consulta con filtro dinámico
$sql = "
SELECT 
    Id_articulo,
    descripcion,
    Marca,
    Rubro,
    Subrubro,
    Venta,
    Stock,
    imagen
FROM articulos
WHERE 
    descripcion LIKE '%$q%' 
    OR Marca LIKE '%$q%' 
    OR Rubro LIKE '%$q%' 
LIMIT 50
";

$resultado = $conexion->query($sql);

if (!$resultado) {
    http_response_code(500);
    echo json_encode(["error" => "Error en la consulta"]);
    exit;
}

// Construcción del resultado
$articulos = [];
while ($fila = $resultado->fetch_assoc()) {
    $articulos[] = $fila;
}

echo json_encode($articulos, JSON_UNESCAPED_UNICODE);
$conexion->close();
?>
