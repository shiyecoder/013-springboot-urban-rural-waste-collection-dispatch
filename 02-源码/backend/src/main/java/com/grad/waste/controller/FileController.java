package com.grad.waste.controller;

import com.grad.waste.common.BizException;
import com.grad.waste.common.R;
import com.grad.waste.common.UserContext;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 文件上传：保存到项目根目录 uploads/yyyyMM/，返回相对路径 /uploads/**。
 * 只允许图片与 PDF，禁止外部 URL。
 */
@RestController
@RequestMapping("/api/file")
public class FileController {

    private static final Set<String> ALLOW = Set.of("jpg", "jpeg", "png", "webp", "pdf");

    @Value("${app.upload-dir:./uploads}")
    private String uploadDir;

    @PostMapping("/upload")
    public R<Map<String, Object>> upload(@RequestParam("file") MultipartFile file) throws Exception {
        if (file == null || file.isEmpty()) throw new BizException("请选择文件");
        String origin = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = origin.contains(".") ? origin.substring(origin.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!ALLOW.contains(ext)) throw new BizException("仅支持 jpg/png/webp/pdf 格式");
        if (file.getSize() > 20L * 1024 * 1024) throw new BizException("单个文件不得超过 20MB");
        String month = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM"));
        Path dir = Paths.get(uploadDir, month).toAbsolutePath().normalize();
        Files.createDirectories(dir);
        String name = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        File target = new File(dir.toFile(), name);
        file.transferTo(target);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("path", "/uploads/" + month + "/" + name);
        m.put("fileName", origin);
        m.put("size", file.getSize());
        m.put("uploader", UserContext.name());
        return R.ok(m);
    }
}
